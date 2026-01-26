"""生成应用图标"""

from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QIcon, QRadialGradient, QBrush
from PyQt6.QtCore import Qt, QPointF


def create_app_icon() -> QIcon:
    """创建应用图标"""
    return create_kafka_icon()


def create_kafka_icon() -> QIcon:
    """创建 Kafka Explorer 风格图标 - 蓝紫渐变球体 + K字母"""
    icon = QIcon()
    
    for size in [16, 32, 48, 64, 128, 256]:
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center = size / 2
        radius = size / 2 - 1
        
        # 创建径向渐变 - 蓝紫色球体效果
        gradient = QRadialGradient(QPointF(center * 0.7, center * 0.5), radius * 1.3)
        gradient.setColorAt(0.0, QColor("#a8c8ff"))    # 高光 - 浅蓝
        gradient.setColorAt(0.3, QColor("#6b8dd6"))    # 蓝色
        gradient.setColorAt(0.6, QColor("#8b7bc7"))    # 蓝紫过渡
        gradient.setColorAt(0.85, QColor("#7d5a9e"))   # 紫色
        gradient.setColorAt(1.0, QColor("#4a3a6b"))    # 深紫阴影
        
        # 绘制球体
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(1, 1, int(radius * 2), int(radius * 2))
        
        # 添加右下角阴影效果
        shadow_gradient = QRadialGradient(QPointF(center * 1.4, center * 1.4), radius * 0.8)
        shadow_gradient.setColorAt(0.0, QColor(80, 40, 60, 120))
        shadow_gradient.setColorAt(1.0, QColor(80, 40, 60, 0))
        painter.setBrush(QBrush(shadow_gradient))
        painter.drawEllipse(1, 1, int(radius * 2), int(radius * 2))
        
        # 绘制 "K" 字母 - 深红褐色
        painter.setPen(QColor("#8B4513"))  # 深褐色
        font_size = max(8, int(size * 0.5))
        font = QFont("Times New Roman", font_size, QFont.Weight.Bold)
        font.setItalic(True)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "K")
        
        painter.end()
        icon.addPixmap(pixmap)
    
    return icon

