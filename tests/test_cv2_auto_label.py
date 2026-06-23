from unittest import TestCase

from ml_models.configs.base import AutoLabelConfig
from ml_models.executors.cv2_auto_label_executor import Cv2AutoLabelExecutor
from ml_models.services.task import TaskManager, MlModelTask

auto_label_executor = Cv2AutoLabelExecutor()

class Cv2AutoLabelExecutorTest(TestCase):

    def test_auto_label(self):
        """测试 Cv2AutoLabelExecutor 的 auto_label 方法"""
        
        # 构建测试的配置
        config = AutoLabelConfig(
            start=True,
            output_dir="tests/output/auto_label",
        )
        manager = TaskManager(MlModelTask(total=100))

        with manager:
            assert auto_label_executor is not None, "AutoLabelExecutor 未正确初始化"
            auto_label_executor.auto_label(manager, config)
