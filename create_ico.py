"""生成 ICO 图标文件"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QRadialGradient, QBrush
from PyQt6.QtCore import Qt, QPointF


def create_icon_pixmap(size: int) -> QPixmap:
    """创建指定尺寸的图标"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    center = size / 2
    radius = size / 2 - 1
    
    # 创建径向渐变 - 蓝紫色球体效果
    gradient = QRadialGradient(QPointF(center * 0.7, center * 0.5), radius * 1.3)
    gradient.setColorAt(0.0, QColor("#a8c8ff"))
    gradient.setColorAt(0.3, QColor("#6b8dd6"))
    gradient.setColorAt(0.6, QColor("#8b7bc7"))
    gradient.setColorAt(0.85, QColor("#7d5a9e"))
    gradient.setColorAt(1.0, QColor("#4a3a6b"))
    
    # 绘制球体
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(gradient))
    painter.drawEllipse(1, 1, int(radius * 2), int(radius * 2))
    
    # 添加阴影
    shadow_gradient = QRadialGradient(QPointF(center * 1.4, center * 1.4), radius * 0.8)
    shadow_gradient.setColorAt(0.0, QColor(80, 40, 60, 120))
    shadow_gradient.setColorAt(1.0, QColor(80, 40, 60, 0))
    painter.setBrush(QBrush(shadow_gradient))
    painter.drawEllipse(1, 1, int(radius * 2), int(radius * 2))
    
    # 绘制 "K" 字母
    painter.setPen(QColor("#8B4513"))
    font_size = max(8, int(size * 0.5))
    font = QFont("Times New Roman", font_size, QFont.Weight.Bold)
    font.setItalic(True)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "K")
    
    painter.end()
    return pixmap


def main():
    app = QApplication(sys.argv)
    
    # 生成多个尺寸的 PNG
    sizes = [16, 32, 48, 64, 128, 256]
    
    for size in sizes:
        pixmap = create_icon_pixmap(size)
        pixmap.save(f"resources/icon_{size}.png", "PNG")
        print(f"已生成: resources/icon_{size}.png")
    
    # 生成主图标
    pixmap = create_icon_pixmap(256)
    pixmap.save("resources/icon.png", "PNG")
    print("已生成: resources/icon.png")
    
    print("\n请使用在线工具将 PNG 转换为 ICO:")
    print("https://convertio.co/png-ico/")
    print("或使用 Pillow: pip install pillow")


if __name__ == "__main__":
    main()

