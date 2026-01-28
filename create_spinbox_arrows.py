"""生成 QSpinBox 上下箭头 PNG（用于样式表 image: url()）"""

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QImage, QPainter, QColor, QPolygonF
from PyQt6.QtCore import QPointF, Qt


def create_arrow_image(up: bool, size_w: int = 12, size_h: int = 8) -> QImage:
    """创建上箭头或下箭头小图，透明背景。"""
    img = QImage(size_w, size_h, QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.transparent)
    painter = QPainter(img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor("#9ca3af"))  # 灰蓝色，暗色/亮色主题下都可见
    cx, cy = size_w / 2.0, size_h / 2.0
    if up:
        # 向上三角形：顶点在上
        poly = QPolygonF([
            QPointF(cx, 1),
            QPointF(size_w - 1, size_h - 1),
            QPointF(1, size_h - 1),
        ])
    else:
        # 向下三角形：顶点在下
        poly = QPolygonF([
            QPointF(1, 1),
            QPointF(size_w - 1, 1),
            QPointF(cx, size_h - 1),
        ])
    painter.drawPolygon(poly)
    painter.end()
    return img


def main():
    app = QApplication(sys.argv)
    res_dir = Path(__file__).parent / "resources"
    res_dir.mkdir(exist_ok=True)
    up_img = create_arrow_image(up=True)
    down_img = create_arrow_image(up=False)
    up_path = res_dir / "up_arrow.png"
    down_path = res_dir / "down_arrow.png"
    up_img.save(str(up_path), "PNG")
    down_img.save(str(down_path), "PNG")
    print(f"已生成: {up_path}")
    print(f"已生成: {down_path}")


if __name__ == "__main__":
    main()
