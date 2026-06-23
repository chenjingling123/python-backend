from __future__ import annotations
import re
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

# ---------- 正则 ----------
# HTML标签清理：非贪婪
_HTML_TAG_RE   = re.compile(r'<.*?>', re.IGNORECASE | re.DOTALL)
# 绝对时间戳： 2025-08-27 13:14:50.787
_TIME_RE       = re.compile(r'\b\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3}\b')

# 字段提取（允许跨行与可变空格）
_LOC_RE        = re.compile(r"\[latitude:\s*([-\d.]+)\]\s*\[longitude:\s*([-\d.]+)\]", re.IGNORECASE | re.DOTALL)
_ALT_RE        = re.compile(r"\[rel_alt:\s*([-\d.]+)\s*abs_alt:\s*([-\d.]+)\]", re.IGNORECASE | re.DOTALL)
# 可选的云台/机体姿态（如果没有就不解析，不报错）
_ATT_RE        = re.compile(r"\[gb_yaw:\s*([-\d.]+)\s*gb_pitch:\s*([-\d.]+)\s*gb_roll:\s*([-\d.]+)\]", re.IGNORECASE | re.DOTALL)

# SRT 时间轴（用于跳过第二行）
_SRT_TIMERANGE = re.compile(r'^\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}$')

def _clean_html_tags(text: str) -> str:
    return _HTML_TAG_RE.sub('', text).strip()

def _calc_time_diff(base_ms: float, start_time_str: str, current_time_str: str) -> float:
    """以第一帧绝对时间为0点，返回 current 相对毫秒；再叠加 base_ms 偏移。"""
    t0 = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S.%f")
    t1 = datetime.strptime(current_time_str, "%Y-%m-%d %H:%M:%S.%f")
    return base_ms + (t1 - t0).total_seconds() * 1000.0

@dataclass
class Telemetry:
    rel_ms: int
    abs_time: str  # ISO 毫秒字符串（yyyy-MM-ddTHH:mm:ss.SSS）
    lat: Optional[float]
    lon: Optional[float]
    rel_alt: Optional[float]
    abs_alt: Optional[float]
    yaw: Optional[float]
    pitch: Optional[float]
    roll: Optional[float]

def _split_srt_blocks(raw: str) -> List[str]:
    """
    将 SRT 按“空行”拆分为块；对每块，通常结构为：
        <index>
        <time range>
        <content...>   # 可能包含 <font ...> 包裹、并跨多行
    """
    # 兼容不同换行：\r\n / \n
    # 用 “至少一个空行” 作为块分隔
    blocks = re.split(r"(?:\r?\n){2,}", raw.strip())
    return [b.strip() for b in blocks if b.strip()]

def _extract_block_payload_lines(block: str) -> List[str]:
    """
    去掉块内的索引行（纯数字）与时间轴行（xx:xx:xx,xxx --> xx:xx:xx,xxx），
    其余作为有效内容返回（可能含 <font> 标签）。
    """
    lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
    if not lines:
        return []

    # 跳过第一行纯数字（序号）
    idx = 0
    if lines and lines[0].isdigit():
        idx = 1

    # 跳过第二行时间轴
    if idx < len(lines) and _SRT_TIMERANGE.match(lines[idx] or ""):
        idx += 1

    return lines[idx:]

def _extract_timestamp_from_lines(payload_lines: List[str]) -> Optional[str]:
    """
    在载荷行中查找第一个绝对时间戳（2025-08-27 13:14:50.787），返回其字符串。
    一般该时间戳是“第二行”，但这里不强依赖行号，直接正则搜索以增强鲁棒性。
    """
    # 拼成一段文本（保留原有换行），但先把 HTML 标签清掉，避免干扰
    payload_text = _clean_html_tags("\n".join(payload_lines))
    m = _TIME_RE.search(payload_text)
    return m.group(0) if m else None

def _extract_fields_from_lines(payload_lines: List[str]):
    """
    在载荷行中提取经纬、高度、可选姿态等字段。字段可能在同一行或跨行。
    """
    payload_text = _clean_html_tags("\n".join(payload_lines))

    lat = lon = rel_alt = abs_alt = yaw = pitch = roll = None

    m = _LOC_RE.search(payload_text)
    if m:
        lat, lon = float(m.group(1)), float(m.group(2))

    m = _ALT_RE.search(payload_text)
    if m:
        rel_alt, abs_alt = float(m.group(1)), float(m.group(2))

    m = _ATT_RE.search(payload_text)
    if m:
        yaw, pitch, roll = float(m.group(1)), float(m.group(2)), float(m.group(3))

    return lat, lon, rel_alt, abs_alt, yaw, pitch, roll

def load_telemetry_from_srt(srt_file: str, base_relative_time: float = 0.0) -> List[Telemetry]:
    """
    解析 DJI 风格的 .srt（与你上传的样式一致）：
    - 支持 <font size="28">…</font>
    - 块内字段可分多行
    - 自动定位绝对时间行
    - 支持 [gb_yaw gb_pitch gb_roll]（若无则返回 None，不报错）

    返回按 rel_ms 升序排列的 Telemetry 列表。
    """
    with open(srt_file, "r", encoding="utf-8") as f:
        raw = f.read()

    blocks = _split_srt_blocks(raw)
    if not blocks:
        return []

    # 第一块中找基准时间
    first_payload = _extract_block_payload_lines(blocks[0])
    initial_time_str = _extract_timestamp_from_lines(first_payload)
    if not initial_time_str:
        # 没有时间无法对齐，直接返回空
        return []

    tele_list: List[Telemetry] = []

    for block in blocks:
        payload_lines = _extract_block_payload_lines(block)
        if not payload_lines:
            continue

        ts_str = _extract_timestamp_from_lines(payload_lines)
        if not ts_str:
            # 该块无法解析时间，跳过
            continue

        rel_ms_f = _calc_time_diff(base_relative_time, initial_time_str, ts_str)
        rel_ms = int(round(rel_ms_f))
        abs_iso = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

        lat, lon, rel_alt, abs_alt, yaw, pitch, roll = _extract_fields_from_lines(payload_lines)

        tele_list.append(Telemetry(
            rel_ms=rel_ms,
            abs_time=abs_iso,
            lat=lat, lon=lon,
            rel_alt=rel_alt, abs_alt=abs_alt,
            yaw=yaw, pitch=pitch, roll=roll
        ))

    tele_list.sort(key=lambda t: t.rel_ms)
    return tele_list

def find_telemetry(tele_list: List[Telemetry], ts_ms: int) -> Optional[Telemetry]:
    """二分查找：返回与 ts_ms 最接近（或恰好对齐）的那条 telemetry。"""
    if not tele_list:
        return None
    lo, hi = 0, len(tele_list) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        v = tele_list[mid].rel_ms
        if ts_ms == v:
            return tele_list[mid]
        if ts_ms < v:
            hi = mid - 1
        else:
            lo = mid + 1
    # 最近邻
    candidates = []
    if 0 <= hi < len(tele_list): candidates.append(tele_list[hi])
    if 0 <= lo < len(tele_list): candidates.append(tele_list[lo])
    if not candidates: return None
    return min(candidates, key=lambda t: abs(t.rel_ms - ts_ms))
