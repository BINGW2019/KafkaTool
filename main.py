#!/usr/bin/env python3
"""
Kafka Explorer - 轻量级 Kafka 集群管理工具

使用方法:
    python main.py

功能:
    - 连接管理: 支持多个 Kafka 集群连接配置
    - Topic 浏览: 查看 Topics 列表、分区信息、配置详情
    - Consumer Groups: 监控消费者组、查看 offset 和 lag
    - 消息浏览: 实时查看 Topic 中的消息内容
    - 消息发送: 向指定 Topic 发送消息
"""

import sys
import logging
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_high_dpi():
    """设置高DPI支持"""
    # PyQt6 默认启用高DPI支持
    pass


def main():
    """主函数"""
    setup_high_dpi()
    
    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName("Kafka Explorer")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("KafkaExplorer")
    
    # 设置应用图标
    from resources import create_kafka_icon
    app.setWindowIcon(create_kafka_icon())
    
    # 设置默认字体
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # 导入并创建主窗口
    from ui import MainWindow
    
    window = MainWindow()
    window.show()
    
    logger.info("Kafka Explorer 已启动")
    
    # 运行应用
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

