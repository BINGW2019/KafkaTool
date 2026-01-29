"""应用样式定义 - Clash Verge 风格深色主题"""

# ==================== 暗色主题 (Clash Verge Style) ====================
DARK_THEME = """
/* ========== 全局样式 ========== */
QWidget {
    background-color: #1a1b2e;
    color: #e1e4eb;
    font-family: 'Segoe UI', 'Microsoft YaHei UI', sans-serif;
    font-size: 13px;
}

/* ========== 主窗口 ========== */
QMainWindow {
    background-color: #1a1b2e;
}

QMainWindow > QWidget {
    background-color: #1a1b2e;
}

/* ========== 左侧导航面板 ========== */
#leftPanel {
    background-color: #1a1b2e;
    border: none;
}

#leftPanel QWidget {
    background-color: #1a1b2e;
}

/* ========== 分割器容器 ========== */
QSplitter {
    background-color: #1a1b2e;
}

QStackedWidget {
    background-color: #1a1b2e;
}

QStackedWidget > QWidget {
    background-color: #1a1b2e;
}

/* ========== 菜单栏 ========== */
QMenuBar {
    background-color: #1a1b2e;
    color: #e1e4eb;
    border-bottom: 1px solid #2a2d47;
    padding: 6px 8px;
}

QMenuBar::item {
    padding: 8px 16px;
    border-radius: 6px;
    margin: 0 2px;
}

QMenuBar::item:selected {
    background-color: #2a2d47;
}

QMenuBar::item:pressed {
    background-color: #3d5afe;
}

QMenu {
    background-color: #1a1b2e;
    border: 1px solid #2a2d47;
    border-radius: 10px;
    padding: 8px;
}

QMenu::item {
    padding: 10px 28px;
    border-radius: 6px;
    margin: 2px 4px;
}

QMenu::item:selected {
    background-color: #3d5afe;
    color: #ffffff;
}

QMenu::separator {
    height: 1px;
    background-color: #2a2d47;
    margin: 6px 12px;
}

/* ========== 工具栏 ========== */
QToolBar {
    background-color: #1a1b2e;
    border: none;
    border-bottom: 1px solid #2a2d47;
    padding: 6px 8px;
    spacing: 6px;
}

QToolButton {
    background-color: transparent;
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    color: #9ca3af;
    font-weight: 500;
}

QToolButton:hover {
    background-color: #252847;
    color: #e1e4eb;
}

QToolButton:pressed {
    background-color: #3d5afe;
    color: #ffffff;
}

QToolButton:checked {
    background-color: transparent;
    color: #9ca3af;
}

QToolButton:focus {
    background-color: transparent;
    outline: none;
}

/* ========== 侧边栏导航树 ========== */
QTreeWidget, QTreeView {
    background-color: #1a1b2e;
    border: none;
    border-radius: 0px;
    padding: 4px;
    outline: none;
    selection-background-color: transparent;
    font-family: 'Segoe UI', 'Segoe UI Emoji', 'Microsoft YaHei UI', sans-serif;
}

QTreeWidget::item, QTreeView::item {
    padding: 10px 8px;
    border-radius: 8px;
    margin: 2px 0;
}

QTreeWidget::item:hover, QTreeView::item:hover {
    background-color: #252847;
}

QTreeWidget::item:selected, QTreeView::item:selected {
    background-color: #3d68b0;
    color: #ffffff;
    font-weight: bold;
}

QTreeWidget::branch {
    background-color: transparent;
}

QTreeWidget::branch:has-children:!has-siblings:closed,
QTreeWidget::branch:closed:has-children:has-siblings {
    border-image: none;
    image: none;
}

QTreeWidget::branch:open:has-children:!has-siblings,
QTreeWidget::branch:open:has-children:has-siblings {
    border-image: none;
    image: none;
}

/* ========== 表格视图 ========== */
QTableWidget, QTableView {
    background-color: #1a1b2e;
    border: 1px solid #2a2d47;
    border-radius: 12px;
    gridline-color: #2a2d47;
    outline: none;
    selection-background-color: #3d5afe;
    alternate-background-color: #1a1b2e;
}

QTableWidget QTableCornerButton::section, QTableView QTableCornerButton::section {
    background-color: #1a1b2e;
    border: none;
}

QTableWidget::item, QTableView::item {
    padding: 16px 12px;
    border: none;
    border-bottom: 1px solid #252847;
    background-color: #1a1b2e;
    color: #e1e4eb;
    min-height: 40px;
}

QTableWidget::item:selected, QTableView::item:selected {
    background-color: #3d5afe;
    color: #ffffff;
}

QTableWidget::item:hover, QTableView::item:hover {
    background-color: #252847;
}

QTableWidget::item:alternate, QTableView::item:alternate {
    background-color: #1a1b2e;
}

QHeaderView::section {
    background-color: #1a1b2e;
    color: #5b9cf4;
    padding: 10px 10px;
    border: none;
    border-bottom: 2px solid #3d5afe;
    font-weight: 600;
    font-size: 12px;
    min-height: 40px;
}

QHeaderView::section:hover {
    background-color: #1a1b2e;
}

QHeaderView::section:first {
    border-top-left-radius: 10px;
}

QHeaderView::section:last {
    border-top-right-radius: 10px;
}

/* ========== 滚动条 ========== */
QScrollBar:vertical {
    background-color: #1a1b2e;
    width: 10px;
    border-radius: 5px;
    margin: 4px 2px;
    border: none;
}

QScrollBar::handle:vertical {
    background-color: #3a3d5c;
    border-radius: 5px;
    min-height: 40px;
    border: none;
}

QScrollBar::handle:vertical:hover {
    background-color: #4a4d6c;
}

QScrollBar::handle:vertical:pressed {
    background-color: #5b9cf4;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
    background: none;
    border: none;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: #1a1b2e;
    border: none;
}

QScrollBar:horizontal {
    background-color: #1a1b2e;
    height: 10px;
    border-radius: 5px;
    margin: 2px 4px;
    border: none;
}

QScrollBar::handle:horizontal {
    background-color: #3a3d5c;
    border-radius: 5px;
    min-width: 40px;
    border: none;
}

QScrollBar::handle:horizontal:hover {
    background-color: #4a4d6c;
}

QScrollBar::handle:horizontal:pressed {
    background-color: #5b9cf4;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
    background: none;
    border: none;
}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: #1a1b2e;
    border: none;
}

/* ========== 分割器 ========== */
QSplitter::handle {
    background-color: #2a2d47;
}

QSplitter::handle:horizontal {
    width: 2px;
}

QSplitter::handle:vertical {
    height: 2px;
}

QSplitter::handle:hover {
    background-color: #3d5afe;
}

/* ========== 输入框 ========== */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #1a1b2e;
    border: 2px solid #2a2d47;
    border-radius: 10px;
    padding: 12px 14px;
    color: #e1e4eb;
    selection-background-color: #3d5afe;
    selection-color: #ffffff;
}

QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover {
    border-color: #3a3d5c;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #5b9cf4;
    background-color: #1a1b2e;
}

QLineEdit:disabled, QTextEdit:disabled {
    background-color: #1a1b2e;
    color: #565f89;
    border-color: #1a1b2e;
}

QLineEdit::placeholder {
    color: #565f89;
}

/* ========== 下拉框 ========== */
QComboBox {
    background-color: #1a1b2e;
    border: 2px solid #2a2d47;
    border-radius: 10px;
    padding: 10px 14px;
    min-width: 100px;
    color: #e1e4eb;
}

QComboBox:hover {
    border-color: #3a3d5c;
}

QComboBox:focus {
    border-color: #5b9cf4;
}

QComboBox::drop-down {
    border: none;
    padding-right: 14px;
    width: 20px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #9ca3af;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #1a1b2e;
    border: 1px solid #2a2d47;
    border-radius: 10px;
    selection-background-color: #3d5afe;
    selection-color: #ffffff;
    padding: 6px;
    outline: none;
}

QComboBox QAbstractItemView::item {
    padding: 10px 14px;
    border-radius: 6px;
    margin: 2px;
}

QComboBox QAbstractItemView::item:hover {
    background-color: #252847;
}

/* ========== 按钮 ========== */
QPushButton {
    background-color: #3d5afe;
    color: #ffffff;
    border: none;
    border-radius: 10px;
    padding: 12px 24px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #5b9cf4;
}

QPushButton:pressed {
    background-color: #2196f3;
}

QPushButton:disabled {
    background-color: #2a2d47;
    color: #565f89;
}

QPushButton[flat="true"] {
    background-color: transparent;
    color: #5b9cf4;
}

QPushButton[flat="true"]:hover {
    background-color: #252847;
}

/* 危险按钮 */
QPushButton[danger="true"] {
    background-color: #f44336;
}

QPushButton[danger="true"]:hover {
    background-color: #ef5350;
}

QPushButton[danger="true"]:pressed {
    background-color: #e53935;
}

/* 次要按钮 */
QPushButton[secondary="true"] {
    background-color: #252847;
    color: #e1e4eb;
}

QPushButton[secondary="true"]:hover {
    background-color: #2f3260;
}

QPushButton[secondary="true"]:pressed {
    background-color: #3d5afe;
}

/* 成功按钮 */
QPushButton[success="true"] {
    background-color: #4caf50;
}

QPushButton[success="true"]:hover {
    background-color: #66bb6a;
}

/* ========== 标签页 ========== */
QTabWidget::pane {
    background-color: #1a1b2e;
    border: 1px solid #2a2d47;
    border-radius: 12px;
    margin-top: -1px;
    padding: 8px;
}

QTabBar {
    background-color: transparent;
}

QTabBar::tab {
    background-color: transparent;
    color: #9ca3af;
    padding: 14px 24px;
    border: none;
    border-bottom: 3px solid transparent;
    margin-right: 4px;
    font-weight: 500;
}

QTabBar::tab:selected {
    color: #5b9cf4;
    border-bottom: 3px solid #5b9cf4;
}

QTabBar::tab:hover:!selected {
    color: #e1e4eb;
    background-color: #252847;
    border-radius: 8px 8px 0 0;
}

/* ========== 分组框 ========== */
QGroupBox {
    background-color: #1a1b2e;
    border: 1px solid #2a2d47;
    border-radius: 12px;
    margin-top: 20px;
    padding: 20px 16px 16px 16px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 14px;
    color: #5b9cf4;
    background-color: #1a1b2e;
    border-radius: 6px;
    margin-left: 10px;
}

/* ========== 复选框 ========== */
QCheckBox {
    spacing: 10px;
    color: #e1e4eb;
}

QCheckBox::indicator {
    width: 22px;
    height: 22px;
    border-radius: 6px;
    border: 2px solid #3a3d5c;
    background-color: #1a1b2e;
}

QCheckBox::indicator:hover {
    border-color: #5b9cf4;
}

QCheckBox::indicator:checked {
    background-color: #3d5afe;
    border-color: #3d5afe;
}

QCheckBox::indicator:checked:hover {
    background-color: #5b9cf4;
    border-color: #5b9cf4;
}

/* ========== 单选按钮 ========== */
QRadioButton {
    spacing: 10px;
    color: #e1e4eb;
}

QRadioButton::indicator {
    width: 22px;
    height: 22px;
    border-radius: 11px;
    border: 2px solid #3a3d5c;
    background-color: #1a1b2e;
}

QRadioButton::indicator:hover {
    border-color: #5b9cf4;
}

QRadioButton::indicator:checked {
    background-color: #3d5afe;
    border-color: #3d5afe;
}

/* ========== 数字输入框 ========== */
QSpinBox, QDoubleSpinBox {
    background-color: #1a1b2e;
    border: 2px solid #2a2d47;
    border-radius: 10px;
    padding: 10px 14px;
    color: #e1e4eb;
}

QSpinBox:hover, QDoubleSpinBox:hover {
    border-color: #3a3d5c;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #5b9cf4;
}

QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    background-color: #252847;
    border: none;
    border-radius: 4px;
    width: 20px;
    min-height: 14px;
    margin: 1px;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover,
QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
    background-color: #3d5afe;
}

QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
    image: url({{RESOURCES_DIR}}/up_arrow.png);
    width: 12px;
    height: 8px;
    subcontrol-origin: padding;
    subcontrol-position: top center;
}

QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
    image: url({{RESOURCES_DIR}}/down_arrow.png);
    width: 12px;
    height: 8px;
    subcontrol-origin: padding;
    subcontrol-position: bottom center;
}

/* ========== 进度条 ========== */
QProgressBar {
    background-color: #252847;
    border: none;
    border-radius: 6px;
    height: 10px;
    text-align: center;
    color: transparent;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #3d5afe, stop:1 #5b9cf4);
    border-radius: 6px;
}

/* ========== 状态栏 ========== */
QStatusBar {
    background-color: #1a1b2e;
    color: #9ca3af;
    border-top: 1px solid #2a2d47;
    padding: 4px 0;
}

QStatusBar::item {
    border: none;
}

/* ========== 对话框 ========== */
QDialog {
    background-color: #1a1b2e;
}

/* ========== 标签 ========== */
QLabel {
    color: #e1e4eb;
}

QLabel[heading="true"] {
    font-size: 20px;
    font-weight: 700;
    color: #5b9cf4;
}

QLabel[subheading="true"] {
    color: #9ca3af;
    font-size: 12px;
}

/* ========== 提示框 ========== */
QToolTip {
    background-color: #1a1b2e;
    color: #e1e4eb;
    border: 1px solid #3d5afe;
    border-radius: 8px;
    padding: 10px 12px;
    font-size: 12px;
}

/* ========== 消息框 ========== */
QMessageBox {
    background-color: #1a1b2e;
}

QMessageBox QLabel {
    color: #e1e4eb;
    font-size: 13px;
}

QMessageBox QPushButton {
    min-width: 80px;
    min-height: 32px;
}

/* ========== 列表视图 ========== */
QListWidget, QListView {
    background-color: #1a1b2e;
    border: 1px solid #2a2d47;
    border-radius: 12px;
    padding: 6px;
    outline: none;
}

QListWidget::item, QListView::item {
    padding: 12px 14px;
    border-radius: 8px;
    margin: 2px;
}

QListWidget::item:hover, QListView::item:hover {
    background-color: #252847;
}

QListWidget::item:selected, QListView::item:selected {
    background-color: #3d5afe;
    color: #ffffff;
}

/* ========== 框架/分隔线 ========== */
QFrame[frameShape="4"] {
    background-color: #2a2d47;
    max-height: 1px;
}

QFrame[frameShape="5"] {
    background-color: #2a2d47;
    max-width: 1px;
}

/* ========== 统计卡片 ========== */
#statsCard {
    background-color: #1a1b2e;
    border: 1px solid #2a2d47;
    border-radius: 16px;
    padding: 20px;
}

#statsCard:hover {
    border-color: #3a3d5c;
    background-color: #1a1b2e;
}

#statsCardTitle {
    color: #9ca3af;
    font-size: 12px;
    font-weight: 500;
}

#statsCardValue {
    color: #5b9cf4;
    font-size: 32px;
    font-weight: bold;
}

/* ========== 功能卡片 ========== */
#featureCard {
    background-color: #1a1b2e;
    border: 1px solid #2a2d47;
    border-radius: 16px;
}

#featureCard:hover {
    border-color: #5b9cf4;
    background-color: #1a1b2e;
}

#featureCardTitle {
    font-size: 14px;
    font-weight: bold;
    color: #e1e4eb;
    background-color: transparent;
}

#featureCardDesc {
    font-size: 12px;
    color: #9ca3af;
    background-color: transparent;
}

/* ========== 自定义状态标签样式 ========== */
QLabel[status="connected"] {
    color: #4caf50;
    font-weight: 600;
}

QLabel[status="disconnected"] {
    color: #f44336;
    font-weight: 600;
}

QLabel[status="warning"] {
    color: #ff9800;
    font-weight: 600;
}
"""

# ==================== 亮色主题 (Light) ====================
LIGHT_THEME = """
/* 全局样式 */
QWidget {
    background-color: #f5f6fa;
    color: #1e293b;
    font-family: 'Segoe UI', 'Microsoft YaHei UI', sans-serif;
    font-size: 13px;
}

/* 主窗口 */
QMainWindow {
    background-color: #f5f6fa;
}

QMainWindow > QWidget {
    background-color: #f5f6fa;
}

/* 左侧导航面板 */
#leftPanel {
    background-color: #f5f6fa;
    border: none;
}

#leftPanel QWidget {
    background-color: #f5f6fa;
}

/* 分割器容器 */
QSplitter {
    background-color: #f5f6fa;
}

QStackedWidget {
    background-color: #f5f6fa;
}

QStackedWidget > QWidget {
    background-color: #f5f6fa;
}

/* 菜单栏 */
QMenuBar {
    background-color: #ffffff;
    color: #1e293b;
    border-bottom: 1px solid #e2e8f0;
    padding: 6px 8px;
}

QMenuBar::item {
    padding: 8px 16px;
    border-radius: 6px;
    margin: 0 2px;
}

QMenuBar::item:selected {
    background-color: #e2e8f0;
}

QMenuBar::item:pressed {
    background-color: #3d5afe;
    color: #ffffff;
}

QMenu {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

QMenu::item {
    padding: 10px 28px;
    border-radius: 6px;
    margin: 2px 4px;
    color: #1e293b;
}

QMenu::item:selected {
    background-color: #3d5afe;
    color: #ffffff;
}

QMenu::separator {
    height: 1px;
    background-color: #e2e8f0;
    margin: 6px 12px;
}

/* 工具栏 */
QToolBar {
    background-color: #ffffff;
    border: none;
    border-bottom: 1px solid #e2e8f0;
    padding: 6px 8px;
    spacing: 6px;
}

QToolButton {
    background-color: transparent;
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    color: #64748b;
    font-weight: 500;
}

QToolButton:hover {
    background-color: #f1f5f9;
    color: #1e293b;
}

QToolButton:pressed {
    background-color: #3d5afe;
    color: #ffffff;
}

/* 树形视图 */
QTreeWidget, QTreeView {
    background-color: #f5f6fa;
    border: none;
    border-radius: 0px;
    padding: 4px;
    outline: none;
    font-family: 'Segoe UI', 'Segoe UI Emoji', 'Microsoft YaHei UI', sans-serif;
}

QTreeWidget::item, QTreeView::item {
    padding: 10px 8px;
    border-radius: 8px;
    margin: 2px 0;
    color: #000000;
    font-weight: bold;
}

QTreeWidget::item:hover, QTreeView::item:hover {
    background-color: #e8f0f8;
}

QTreeWidget::item:selected, QTreeView::item:selected {
    background-color: #c8e0f8;
    color: #000000;
    font-weight: bold;
}

/* 表格视图 */
QTableWidget, QTableView {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    gridline-color: #e2e8f0;
    outline: none;
}

QTableWidget::item, QTableView::item {
    padding: 10px 12px;
    border: none;
    border-bottom: 1px solid #f1f5f9;
    color: #1e293b;
}

QTableWidget::item:selected, QTableView::item:selected {
    background-color: #3d5afe;
    color: #ffffff;
}

QTableWidget::item:hover, QTableView::item:hover {
    background-color: #f8fafc;
}

QHeaderView::section {
    background-color: #f8fafc;
    color: #3d5afe;
    padding: 12px 10px;
    border: none;
    border-bottom: 2px solid #3d5afe;
    font-weight: 600;
    font-size: 12px;
}

QHeaderView::section:hover {
    background-color: #f1f5f9;
}

/* 滚动条 */
QScrollBar:vertical {
    background-color: transparent;
    width: 10px;
    border-radius: 5px;
    margin: 4px 2px;
}

QScrollBar::handle:vertical {
    background-color: #cbd5e1;
    border-radius: 5px;
    min-height: 40px;
}

QScrollBar::handle:vertical:hover {
    background-color: #94a3b8;
}

QScrollBar::handle:vertical:pressed {
    background-color: #3d5afe;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: transparent;
    height: 10px;
    border-radius: 5px;
    margin: 2px 4px;
}

QScrollBar::handle:horizontal {
    background-color: #cbd5e1;
    border-radius: 5px;
    min-width: 40px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #94a3b8;
}

/* 分割器 */
QSplitter::handle {
    background-color: #e2e8f0;
}

QSplitter::handle:horizontal {
    width: 2px;
}

QSplitter::handle:vertical {
    height: 2px;
}

QSplitter::handle:hover {
    background-color: #3d5afe;
}

/* 输入框 */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #ffffff;
    border: 2px solid #e2e8f0;
    border-radius: 10px;
    padding: 12px 14px;
    color: #1e293b;
    selection-background-color: #3d5afe;
    selection-color: #ffffff;
}

QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover {
    border-color: #cbd5e1;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #3d5afe;
    background-color: #ffffff;
}

QLineEdit:disabled, QTextEdit:disabled {
    background-color: #f1f5f9;
    color: #94a3b8;
}

/* 下拉框 */
QComboBox {
    background-color: #ffffff;
    border: 2px solid #e2e8f0;
    border-radius: 10px;
    padding: 10px 14px;
    min-width: 100px;
    color: #1e293b;
}

QComboBox:hover {
    border-color: #cbd5e1;
}

QComboBox:focus {
    border-color: #3d5afe;
}

QComboBox::drop-down {
    border: none;
    padding-right: 14px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #64748b;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    selection-background-color: #3d5afe;
    selection-color: #ffffff;
    padding: 6px;
}

/* 按钮 */
QPushButton {
    background-color: #3d5afe;
    color: #ffffff;
    border: none;
    border-radius: 10px;
    padding: 12px 24px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #536dfe;
}

QPushButton:pressed {
    background-color: #304ffe;
}

QPushButton:disabled {
    background-color: #e2e8f0;
    color: #94a3b8;
}

QPushButton[flat="true"] {
    background-color: transparent;
    color: #3d5afe;
}

QPushButton[flat="true"]:hover {
    background-color: #f1f5f9;
}

/* 危险按钮 */
QPushButton[danger="true"] {
    background-color: #ef4444;
}

QPushButton[danger="true"]:hover {
    background-color: #f87171;
}

/* 次要按钮 */
QPushButton[secondary="true"] {
    background-color: #e2e8f0;
    color: #1e293b;
}

QPushButton[secondary="true"]:hover {
    background-color: #cbd5e1;
}

/* 标签页 */
QTabWidget::pane {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    margin-top: -1px;
    padding: 8px;
}

QTabBar::tab {
    background-color: transparent;
    color: #64748b;
    padding: 14px 24px;
    border: none;
    border-bottom: 3px solid transparent;
    margin-right: 4px;
    font-weight: 500;
}

QTabBar::tab:selected {
    color: #3d5afe;
    border-bottom: 3px solid #3d5afe;
}

QTabBar::tab:hover:!selected {
    color: #1e293b;
    background-color: #f1f5f9;
    border-radius: 8px 8px 0 0;
}

/* 分组框 */
QGroupBox {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    margin-top: 20px;
    padding: 20px 16px 16px 16px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 14px;
    color: #3d5afe;
    background-color: #ffffff;
    border-radius: 6px;
    margin-left: 10px;
}

/* 复选框 */
QCheckBox {
    spacing: 10px;
    color: #1e293b;
}

QCheckBox::indicator {
    width: 22px;
    height: 22px;
    border-radius: 6px;
    border: 2px solid #cbd5e1;
    background-color: #ffffff;
}

QCheckBox::indicator:hover {
    border-color: #3d5afe;
}

QCheckBox::indicator:checked {
    background-color: #3d5afe;
    border-color: #3d5afe;
}

/* 单选按钮 */
QRadioButton {
    spacing: 10px;
    color: #1e293b;
}

QRadioButton::indicator {
    width: 22px;
    height: 22px;
    border-radius: 11px;
    border: 2px solid #cbd5e1;
    background-color: #ffffff;
}

QRadioButton::indicator:hover {
    border-color: #3d5afe;
}

QRadioButton::indicator:checked {
    background-color: #3d5afe;
    border-color: #3d5afe;
}

/* 数字输入框 */
QSpinBox, QDoubleSpinBox {
    background-color: #ffffff;
    border: 2px solid #e2e8f0;
    border-radius: 10px;
    padding: 10px 14px;
    color: #1e293b;
}

QSpinBox:hover, QDoubleSpinBox:hover {
    border-color: #cbd5e1;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #3d5afe;
}

QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    background-color: #f1f5f9;
    border: none;
    border-radius: 4px;
    width: 20px;
    min-height: 12px;
    margin: 1px;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover,
QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
    background-color: #3d5afe;
}

QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
    image: url({{RESOURCES_DIR}}/up_arrow.png);
    width: 12px;
    height: 8px;
    subcontrol-origin: padding;
    subcontrol-position: top center;
}

QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
    image: url({{RESOURCES_DIR}}/down_arrow.png);
    width: 12px;
    height: 8px;
    subcontrol-origin: padding;
    subcontrol-position: bottom center;
}

/* 进度条 */
QProgressBar {
    background-color: #e2e8f0;
    border: none;
    border-radius: 6px;
    height: 10px;
    text-align: center;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #3d5afe, stop:1 #5b9cf4);
    border-radius: 6px;
}

/* 状态栏 */
QStatusBar {
    background-color: #ffffff;
    color: #64748b;
    border-top: 1px solid #e2e8f0;
}

QStatusBar::item {
    border: none;
}

/* 对话框 */
QDialog {
    background-color: #f5f6fa;
}

/* 标签 */
QLabel {
    color: #1e293b;
}

QLabel[heading="true"] {
    font-size: 20px;
    font-weight: 700;
    color: #3d5afe;
}

QLabel[subheading="true"] {
    color: #64748b;
    font-size: 12px;
}

/* 提示框 */
QToolTip {
    background-color: #1e293b;
    color: #ffffff;
    border: 1px solid #3d5afe;
    border-radius: 8px;
    padding: 10px 12px;
}

/* 消息框 */
QMessageBox {
    background-color: #f5f6fa;
}

QMessageBox QLabel {
    color: #1e293b;
}

/* 列表视图 */
QListWidget, QListView {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 6px;
    outline: none;
}

QListWidget::item, QListView::item {
    padding: 12px 14px;
    border-radius: 8px;
    margin: 2px;
    color: #1e293b;
}

QListWidget::item:hover, QListView::item:hover {
    background-color: #f1f5f9;
}

QListWidget::item:selected, QListView::item:selected {
    background-color: #3d5afe;
    color: #ffffff;
}

/* 框架 */
QFrame[frameShape="4"] {
    background-color: #e2e8f0;
    max-height: 1px;
}

QFrame[frameShape="5"] {
    background-color: #e2e8f0;
    max-width: 1px;
}

/* 统计卡片 */
#statsCard {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 20px;
}

#statsCard:hover {
    border-color: #cbd5e1;
    background-color: #f8fafc;
}

#statsCardTitle {
    color: #64748b;
    font-size: 12px;
    font-weight: 500;
}

#statsCardValue {
    color: #3d5afe;
    font-size: 32px;
    font-weight: bold;
}

/* 功能卡片 */
#featureCard {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
}

#featureCard:hover {
    border-color: #3d5afe;
    background-color: #f8fafc;
}

#featureCardTitle {
    font-size: 14px;
    font-weight: bold;
    color: #1e293b;
    background-color: transparent;
}

#featureCardDesc {
    font-size: 12px;
    color: #64748b;
    background-color: transparent;
}
"""

# 主题字典
THEMES = {
    'dark': DARK_THEME,
    'light': LIGHT_THEME
}

# 图标颜色 - Clash Verge 风格
ICON_COLORS = {
    'primary': '#5b9cf4',      # 主色 - 亮蓝色
    'success': '#4caf50',      # 成功 - 绿色
    'warning': '#ff9800',      # 警告 - 橙色
    'danger': '#f44336',       # 危险 - 红色
    'info': '#00bcd4',         # 信息 - 青色
    'muted': '#9ca3af',        # 禁用 - 灰色
    'accent': '#3d5afe'        # 强调色 - 深蓝色
}
