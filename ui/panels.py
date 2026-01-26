"""面板组件"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QSplitter, QTextEdit,
    QPushButton, QSpinBox, QComboBox, QLineEdit, QGroupBox,
    QProgressBar, QFrame, QTabWidget, QTreeWidget, QTreeWidgetItem,
    QMessageBox, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QColor, QAction

from typing import List, Optional
from kafka_client.models import (
    TopicInfo, PartitionInfo, ConsumerGroupInfo, KafkaMessage
)


class LoadingOverlay(QWidget):
    """加载遮罩层"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVisible(False)
        self._theme = "dark"
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.label = QLabel("加载中...")
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.progress = QProgressBar()
        self.progress.setMaximum(0)
        self.progress.setMinimum(0)
        self.progress.setFixedWidth(200)
        layout.addWidget(self.progress, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.apply_theme("dark")
    
    def apply_theme(self, theme: str):
        """应用主题样式"""
        self._theme = theme
        if theme == "dark":
            self.setStyleSheet("background-color: rgba(26, 27, 46, 220);")
            self.label.setStyleSheet("font-size: 16px; color: #5b9cf4; font-weight: 500;")
        else:
            self.setStyleSheet("background-color: rgba(245, 246, 250, 230);")
            self.label.setStyleSheet("font-size: 16px; color: #3d5afe; font-weight: 500;")
    
    def show_loading(self, message: str = "加载中..."):
        self.label.setText(message)
        self.setVisible(True)
        self.raise_()
    
    def hide_loading(self):
        self.setVisible(False)


class StatsCard(QFrame):
    """统计卡片"""
    
    def __init__(self, title: str, value: str = "0", icon: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("statsCard")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        self.title_label = QLabel(title)
        self.title_label.setObjectName("statsCardTitle")
        layout.addWidget(self.title_label)
        
        self.value_label = QLabel(value)
        self.value_label.setObjectName("statsCardValue")
        layout.addWidget(self.value_label)
    
    def set_value(self, value: str):
        self.value_label.setText(value)


class TopicDetailPanel(QWidget):
    """Topic详情面板"""
    
    message_browse_requested = pyqtSignal(str, int)  # topic, partition
    send_message_requested = pyqtSignal(str)  # topic
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_topic: Optional[TopicInfo] = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题栏
        header = QHBoxLayout()
        
        self.title_label = QLabel("Topic 详情")
        self.title_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #5b9cf4;")
        header.addWidget(self.title_label)
        
        header.addStretch()
        
        self.browse_messages_btn = QPushButton("📨 查看消息")
        self.browse_messages_btn.clicked.connect(self.on_browse_messages_clicked)
        header.addWidget(self.browse_messages_btn)
        
        self.send_message_btn = QPushButton("✉️ 发送消息")
        self.send_message_btn.setProperty("secondary", True)
        header.addWidget(self.send_message_btn)
        
        self.refresh_btn = QPushButton("🔄 刷新")
        self.refresh_btn.setProperty("secondary", True)
        header.addWidget(self.refresh_btn)
        
        layout.addLayout(header)
        
        # 统计卡片
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)
        
        self.partitions_card = StatsCard("分区数")
        stats_layout.addWidget(self.partitions_card)
        
        self.messages_card = StatsCard("消息总数")
        stats_layout.addWidget(self.messages_card)
        
        self.replication_card = StatsCard("副本因子")
        stats_layout.addWidget(self.replication_card)
        
        layout.addLayout(stats_layout)
        
        # 标签页
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # 分区信息表格
        partitions_tab = QWidget()
        partitions_layout = QVBoxLayout(partitions_tab)
        partitions_layout.setContentsMargins(0, 16, 0, 0)
        
        self.partitions_table = QTableWidget()
        self.partitions_table.setColumnCount(6)
        self.partitions_table.setHorizontalHeaderLabels([
            "分区ID", "Leader", "副本", "ISR", "起始Offset", "结束Offset"
        ])
        self.partitions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.partitions_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.partitions_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.partitions_table.customContextMenuRequested.connect(self.show_partition_menu)
        partitions_layout.addWidget(self.partitions_table)
        
        tab_widget.addTab(partitions_tab, "分区信息")
        
        # 配置信息表格
        config_tab = QWidget()
        config_layout = QVBoxLayout(config_tab)
        config_layout.setContentsMargins(0, 16, 0, 0)
        
        self.config_table = QTableWidget()
        self.config_table.setColumnCount(2)
        self.config_table.setHorizontalHeaderLabels(["配置项", "值"])
        self.config_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        config_layout.addWidget(self.config_table)
        
        tab_widget.addTab(config_tab, "配置信息")
        
        # 连接发送消息按钮
        self.send_message_btn.clicked.connect(self.on_send_message_clicked)
    
    def on_browse_messages_clicked(self):
        """查看消息按钮点击"""
        if self.current_topic:
            self.message_browse_requested.emit(self.current_topic.name, -1)
    
    def on_send_message_clicked(self):
        """发送消息按钮点击"""
        if self.current_topic:
            self.send_message_requested.emit(self.current_topic.name)
    
    def show_partition_menu(self, pos):
        """显示分区右键菜单"""
        item = self.partitions_table.itemAt(pos)
        if item and self.current_topic:
            menu = QMenu(self)
            browse_action = menu.addAction("浏览消息")
            action = menu.exec(self.partitions_table.mapToGlobal(pos))
            
            if action == browse_action:
                row = item.row()
                partition_id = int(self.partitions_table.item(row, 0).text())
                self.message_browse_requested.emit(self.current_topic.name, partition_id)
    
    def load_topic(self, topic: TopicInfo):
        """加载Topic信息"""
        self.current_topic = topic
        self.title_label.setText(f"Topic: {topic.name}")
        
        # 更新统计卡片
        self.partitions_card.set_value(str(topic.partition_count))
        self.messages_card.set_value(f"{topic.total_messages:,}")
        self.replication_card.set_value(str(topic.replication_factor))
        
        # 更新分区表格
        self.partitions_table.setRowCount(len(topic.partitions))
        for i, partition in enumerate(topic.partitions):
            self.partitions_table.setItem(i, 0, QTableWidgetItem(str(partition.partition_id)))
            self.partitions_table.setItem(i, 1, QTableWidgetItem(str(partition.leader)))
            self.partitions_table.setItem(i, 2, QTableWidgetItem(str(partition.replicas)))
            self.partitions_table.setItem(i, 3, QTableWidgetItem(str(partition.isr)))
            self.partitions_table.setItem(i, 4, QTableWidgetItem(f"{partition.beginning_offset:,}"))
            self.partitions_table.setItem(i, 5, QTableWidgetItem(f"{partition.end_offset:,}"))
            # 设置行高
            self.partitions_table.setRowHeight(i, 40)
        
        # 更新配置表格
        self.config_table.setRowCount(len(topic.config))
        for i, (key, value) in enumerate(topic.config.items()):
            self.config_table.setItem(i, 0, QTableWidgetItem(key))
            self.config_table.setItem(i, 1, QTableWidgetItem(str(value)))
            # 设置行高
            self.config_table.setRowHeight(i, 40)
    
    def clear(self):
        """清空面板"""
        self.current_topic = None
        self.title_label.setText("Topic 详情")
        self.partitions_card.set_value("0")
        self.messages_card.set_value("0")
        self.replication_card.set_value("0")
        self.partitions_table.setRowCount(0)
        self.config_table.setRowCount(0)


class ConsumerGroupPanel(QWidget):
    """消费者组面板"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_group: Optional[ConsumerGroupInfo] = None
        self.all_offsets = []  # 保存所有offset用于过滤
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题栏
        header = QHBoxLayout()
        
        self.title_label = QLabel("Consumer Group 详情")
        self.title_label.setObjectName("statsCardValue")
        header.addWidget(self.title_label)
        
        header.addStretch()
        
        self.refresh_btn = QPushButton("🔄 刷新")
        self.refresh_btn.setProperty("secondary", True)
        header.addWidget(self.refresh_btn)
        
        layout.addLayout(header)
        
        # 统计卡片
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)
        
        self.state_card = StatsCard("状态")
        stats_layout.addWidget(self.state_card)
        
        self.members_card = StatsCard("成员数")
        stats_layout.addWidget(self.members_card)
        
        self.lag_card = StatsCard("总延迟")
        stats_layout.addWidget(self.lag_card)
        
        self.topics_card = StatsCard("Topics")
        stats_layout.addWidget(self.topics_card)
        
        layout.addLayout(stats_layout)
        
        # 标签页
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Offset信息表格
        offsets_tab = QWidget()
        offsets_layout = QVBoxLayout(offsets_tab)
        offsets_layout.setContentsMargins(0, 8, 0, 0)
        
        # 过滤器
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("🔍 过滤:"))
        self.offset_filter_edit = QLineEdit()
        self.offset_filter_edit.setPlaceholderText("输入 Topic 名称过滤...")
        self.offset_filter_edit.textChanged.connect(self.filter_offsets)
        self.offset_filter_edit.setMaximumWidth(300)
        filter_layout.addWidget(self.offset_filter_edit)
        
        self.offset_count_label = QLabel("")
        self.offset_count_label.setObjectName("statsCardTitle")
        filter_layout.addWidget(self.offset_count_label)
        
        filter_layout.addStretch()
        offsets_layout.addLayout(filter_layout)
        
        self.offsets_table = QTableWidget()
        self.offsets_table.setColumnCount(7)
        self.offsets_table.setHorizontalHeaderLabels([
            "Topic", "分区", "Start", "End", "Offset", "Lag", "Lag%"
        ])
        self.offsets_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.offsets_table.horizontalHeader().setStretchLastSection(True)
        self.offsets_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.offsets_table.setSortingEnabled(True)
        offsets_layout.addWidget(self.offsets_table)
        
        tab_widget.addTab(offsets_tab, "Offset 状态")
        
        # 成员信息表格
        members_tab = QWidget()
        members_layout = QVBoxLayout(members_tab)
        members_layout.setContentsMargins(0, 16, 0, 0)
        
        self.members_table = QTableWidget()
        self.members_table.setColumnCount(4)
        self.members_table.setHorizontalHeaderLabels([
            "Member ID", "Client ID", "Host", "分配的分区"
        ])
        self.members_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.members_table.horizontalHeader().setStretchLastSection(True)
        members_layout.addWidget(self.members_table)
        
        tab_widget.addTab(members_tab, "成员信息")
    
    def load_group(self, group: ConsumerGroupInfo):
        """加载消费者组信息"""
        self.current_group = group
        self.all_offsets = group.offsets
        self.title_label.setText(f"Consumer Group: {group.group_id}")
        
        # 更新统计卡片 - Clash Verge 风格颜色
        state_color = "#4caf50" if group.state == "Stable" else "#ff9800"
        self.state_card.set_value(group.state)
        self.state_card.value_label.setStyleSheet(f"color: {state_color}; font-size: 28px; font-weight: bold;")
        
        self.members_card.set_value(str(group.member_count))
        
        lag_color = "#4caf50" if group.total_lag < 1000 else "#f44336" if group.total_lag > 10000 else "#ff9800"
        self.lag_card.set_value(f"{group.total_lag:,}")
        self.lag_card.value_label.setStyleSheet(f"color: {lag_color}; font-size: 28px; font-weight: bold;")
        
        # 统计 Topics 数量
        topics = set(o.topic for o in group.offsets)
        self.topics_card.set_value(str(len(topics)))
        
        # 清空过滤器并显示所有数据
        self.offset_filter_edit.clear()
        self.display_offsets(group.offsets)
        
        # 更新成员表格
        self.members_table.setRowCount(len(group.members))
        for i, member in enumerate(group.members):
            self.members_table.setItem(i, 0, QTableWidgetItem(member.member_id[:30] + "..." if len(member.member_id) > 30 else member.member_id))
            self.members_table.setItem(i, 1, QTableWidgetItem(member.client_id))
            self.members_table.setItem(i, 2, QTableWidgetItem(member.client_host))
            
            partitions_str = ", ".join([
                f"{p['topic']}:{p['partition']}" for p in member.assigned_partitions
            ])
            self.members_table.setItem(i, 3, QTableWidgetItem(partitions_str))
            # 设置行高
            self.members_table.setRowHeight(i, 40)
    
    def filter_offsets(self, text: str):
        """过滤 Offset 列表"""
        text = text.lower().strip()
        if not text:
            filtered = self.all_offsets
        else:
            filtered = [o for o in self.all_offsets if text in o.topic.lower()]
        self.display_offsets(filtered)
    
    def display_offsets(self, offsets):
        """显示 Offset 列表"""
        self.offsets_table.setSortingEnabled(False)
        self.offsets_table.setRowCount(len(offsets))
        
        for i, offset in enumerate(offsets):
            self.offsets_table.setItem(i, 0, QTableWidgetItem(offset.topic))
            
            # 分区 - 数字排序
            partition_item = QTableWidgetItem()
            partition_item.setData(Qt.ItemDataRole.DisplayRole, offset.partition)
            self.offsets_table.setItem(i, 1, partition_item)
            
            # Start Offset
            start_item = QTableWidgetItem()
            start_offset = offset.end_offset - offset.current_offset - offset.lag if hasattr(offset, 'start_offset') else 0
            start_item.setData(Qt.ItemDataRole.DisplayRole, getattr(offset, 'start_offset', 0))
            self.offsets_table.setItem(i, 2, start_item)
            
            # End Offset
            end_item = QTableWidgetItem()
            end_item.setData(Qt.ItemDataRole.DisplayRole, offset.end_offset)
            self.offsets_table.setItem(i, 3, end_item)
            
            # Current Offset
            current_item = QTableWidgetItem()
            current_item.setData(Qt.ItemDataRole.DisplayRole, offset.current_offset)
            self.offsets_table.setItem(i, 4, current_item)
            
            # Lag - 带颜色 (Clash Verge 风格)
            lag_item = QTableWidgetItem()
            lag_item.setData(Qt.ItemDataRole.DisplayRole, offset.lag)
            if offset.lag > 10000:
                lag_item.setForeground(QColor("#f44336"))  # 红色 - 严重
            elif offset.lag > 1000:
                lag_item.setForeground(QColor("#ff9800"))  # 橙色 - 警告
            else:
                lag_item.setForeground(QColor("#4caf50"))  # 绿色 - 正常
            self.offsets_table.setItem(i, 5, lag_item)
            
            # Lag 百分比
            total_messages = offset.end_offset - getattr(offset, 'start_offset', 0)
            if total_messages > 0:
                lag_percent = (offset.lag / total_messages) * 100
                lag_percent_str = f"{lag_percent:.1f}%"
            else:
                lag_percent_str = "0%"
            self.offsets_table.setItem(i, 6, QTableWidgetItem(lag_percent_str))
            # 设置行高
            self.offsets_table.setRowHeight(i, 40)
        
        self.offsets_table.setSortingEnabled(True)
        self.offsets_table.resizeColumnsToContents()
        
        # 更新计数
        total = len(self.all_offsets)
        filtered = len(offsets)
        if filtered == total:
            self.offset_count_label.setText(f"共 {total} 条")
        else:
            self.offset_count_label.setText(f"匹配 {filtered} / {total} 条")
    
    def clear(self):
        """清空面板"""
        self.current_group = None
        self.all_offsets = []
        self.title_label.setText("Consumer Group 详情")
        self.state_card.set_value("-")
        self.members_card.set_value("0")
        self.lag_card.set_value("0")
        self.topics_card.set_value("0")
        self.offsets_table.setRowCount(0)
        self.members_table.setRowCount(0)


class MessageBrowserPanel(QWidget):
    """消息浏览器面板"""
    
    refresh_requested = pyqtSignal(str, int, int, int, bool, str)  # topic, partition, offset, limit, from_beginning, sort_field
    resend_message_requested = pyqtSignal(str, object, object, object)  # topic, key, value, headers
    check_consumption_requested = pyqtSignal(str, int, int, object)  # topic, partition, offset, callback
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.messages: List[KafkaMessage] = []
        self.filtered_messages: List[KafkaMessage] = []
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题栏
        header = QHBoxLayout()
        
        self.title_label = QLabel("消息浏览器")
        self.title_label.setObjectName("statsCardValue")
        header.addWidget(self.title_label)
        
        layout.addLayout(header)
        
        # 获取消息过滤器
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(12)
        
        filter_layout.addWidget(QLabel("Topic:"))
        self.topic_edit = QLineEdit()
        self.topic_edit.setPlaceholderText("输入Topic名称")
        filter_layout.addWidget(self.topic_edit)
        
        filter_layout.addWidget(QLabel("分区:"))
        self.partition_spin = QSpinBox()
        self.partition_spin.setRange(-1, 1000)
        self.partition_spin.setValue(-1)
        self.partition_spin.setSpecialValueText("全部")
        filter_layout.addWidget(self.partition_spin)
        
        filter_layout.addWidget(QLabel("数量:"))
        self.limit_spin = QSpinBox()
        self.limit_spin.setRange(10, 1000)
        self.limit_spin.setValue(100)
        filter_layout.addWidget(self.limit_spin)
        
        filter_layout.addWidget(QLabel("排序:"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["最新", "最旧"])
        self.sort_combo.setMinimumWidth(70)
        filter_layout.addWidget(self.sort_combo)
        
        filter_layout.addWidget(QLabel("按:"))
        self.sort_field_combo = QComboBox()
        self.sort_field_combo.addItems(["Offset", "时间戳"])
        self.sort_field_combo.setMinimumWidth(80)
        filter_layout.addWidget(self.sort_field_combo)
        
        self.fetch_btn = QPushButton("获取消息")
        self.fetch_btn.clicked.connect(self.on_fetch_clicked)
        filter_layout.addWidget(self.fetch_btn)
        
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # 消息内容过滤器
        search_layout = QHBoxLayout()
        search_layout.setSpacing(12)
        
        search_layout.addWidget(QLabel("🔍 过滤:"))
        self.search_key_edit = QLineEdit()
        self.search_key_edit.setPlaceholderText("Key 关键词")
        self.search_key_edit.textChanged.connect(self.filter_messages)
        self.search_key_edit.setMaximumWidth(150)
        search_layout.addWidget(self.search_key_edit)
        
        self.search_value_edit = QLineEdit()
        self.search_value_edit.setPlaceholderText("Value 关键词")
        self.search_value_edit.textChanged.connect(self.filter_messages)
        search_layout.addWidget(self.search_value_edit)
        
        self.match_count_label = QLabel("")
        self.match_count_label.setObjectName("statsCardTitle")
        search_layout.addWidget(self.match_count_label)
        
        search_layout.addStretch()
        
        layout.addLayout(search_layout)
        
        # 分割视图
        splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(splitter)
        
        # 消息列表
        self.messages_table = QTableWidget()
        self.messages_table.setColumnCount(5)
        self.messages_table.setHorizontalHeaderLabels([
            "分区", "Offset", "时间戳", "Key", "Value (预览)"
        ])
        self.messages_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.messages_table.horizontalHeader().setStretchLastSection(True)
        self.messages_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.messages_table.selectionModel().selectionChanged.connect(self.on_message_selected)
        self.messages_table.doubleClicked.connect(self.on_message_double_clicked)
        splitter.addWidget(self.messages_table)
        
        # 消息详情
        detail_widget = QWidget()
        detail_layout = QVBoxLayout(detail_widget)
        detail_layout.setContentsMargins(0, 0, 0, 0)
        
        detail_label = QLabel("消息详情")
        detail_label.setStyleSheet("font-weight: bold; color: #5b9cf4; font-size: 14px;")
        detail_layout.addWidget(detail_label)
        
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setPlaceholderText("选择一条消息查看详情")
        detail_layout.addWidget(self.detail_text)
        
        splitter.addWidget(detail_widget)
        splitter.setSizes([400, 200])
    
    def set_topic(self, topic: str, partition: int = -1):
        """设置Topic"""
        self.topic_edit.setText(topic)
        self.partition_spin.setValue(partition)
        self.title_label.setText(f"消息浏览器 - {topic}")
    
    def on_fetch_clicked(self):
        """获取消息"""
        topic = self.topic_edit.text().strip()
        if not topic:
            QMessageBox.warning(self, "警告", "请输入Topic名称")
            return
        
        partition = self.partition_spin.value()
        limit = self.limit_spin.value()
        from_beginning = self.sort_combo.currentIndex() == 1  # "最旧" = True
        sort_field = "offset" if self.sort_field_combo.currentIndex() == 0 else "timestamp"
        
        self.refresh_requested.emit(topic, partition, -1, limit, from_beginning, sort_field)
    
    def load_messages(self, messages: List[KafkaMessage]):
        """加载消息列表"""
        self.messages = messages
        self.filtered_messages = messages.copy()
        
        # 清空过滤条件
        self.search_key_edit.clear()
        self.search_value_edit.clear()
        
        self.display_messages(self.filtered_messages)
        self.update_match_count()
    
    def filter_messages(self):
        """根据关键词过滤消息"""
        key_filter = self.search_key_edit.text().lower().strip()
        value_filter = self.search_value_edit.text().lower().strip()
        
        if not key_filter and not value_filter:
            self.filtered_messages = self.messages.copy()
        else:
            self.filtered_messages = []
            for msg in self.messages:
                key_match = not key_filter or key_filter in msg.key_str().lower()
                value_match = not value_filter or value_filter in msg.value_str().lower()
                
                if key_match and value_match:
                    self.filtered_messages.append(msg)
        
        self.display_messages(self.filtered_messages)
        self.update_match_count()
    
    def update_match_count(self):
        """更新匹配计数"""
        total = len(self.messages)
        filtered = len(self.filtered_messages)
        
        if filtered == total:
            self.match_count_label.setText(f"共 {total} 条")
        else:
            self.match_count_label.setText(f"匹配 {filtered} / {total} 条")
    
    def display_messages(self, messages: List[KafkaMessage]):
        """显示消息列表"""
        self.messages_table.setRowCount(len(messages))
        
        for i, msg in enumerate(messages):
            self.messages_table.setItem(i, 0, QTableWidgetItem(str(msg.partition)))
            self.messages_table.setItem(i, 1, QTableWidgetItem(str(msg.offset)))
            self.messages_table.setItem(i, 2, QTableWidgetItem(msg.timestamp_str))
            self.messages_table.setItem(i, 3, QTableWidgetItem(msg.key_str()[:50]))
            
            # Value预览(截取前100字符)
            value_preview = msg.value_str()[:100].replace('\n', ' ')
            if len(msg.value_str()) > 100:
                value_preview += "..."
            self.messages_table.setItem(i, 4, QTableWidgetItem(value_preview))
            
            # 设置行高
            self.messages_table.setRowHeight(i, 40)
        
        # 调整列宽
        self.messages_table.resizeColumnsToContents()
    
    def on_message_selected(self):
        """消息选中事件"""
        rows = self.messages_table.selectionModel().selectedRows()
        if rows and self.filtered_messages:
            row = rows[0].row()
            if row < len(self.filtered_messages):
                msg = self.filtered_messages[row]
                
                detail = f"""Topic: {msg.topic}
分区: {msg.partition}
Offset: {msg.offset}
时间戳: {msg.timestamp_str}

=== Key ===
{msg.key_str()}

=== Value ===
{msg.value_str()}

=== Headers ===
{dict(msg.headers) if msg.headers else '无'}
"""
                self.detail_text.setPlainText(detail)
    
    def on_message_double_clicked(self, index):
        """消息双击事件 - 弹出详情对话框"""
        row = index.row()
        if row < len(self.filtered_messages):
            msg = self.filtered_messages[row]
            from .dialogs import MessageDetailDialog
            self._current_dialog = MessageDetailDialog(self, msg)
            self._current_dialog.resend_requested.connect(self.on_resend_requested)
            self._current_dialog.check_consumption_requested.connect(self.on_check_consumption_requested)
            # 连接信号后再请求检查消费状态
            self._current_dialog.request_consumption_check()
            self._current_dialog.exec()
    
    def on_resend_requested(self, topic, key, value, headers):
        """转发重新发送请求"""
        self.resend_message_requested.emit(topic, key, value, headers)
    
    def on_check_consumption_requested(self, topic, partition, offset):
        """转发检查消费状态请求"""
        self.check_consumption_requested.emit(topic, partition, offset, self._update_dialog_consumption_status)
    
    def _update_dialog_consumption_status(self, consumed_by):
        """更新对话框的消费状态"""
        if hasattr(self, '_current_dialog') and self._current_dialog:
            self._current_dialog.update_consumption_status(consumed_by)
    
    def clear(self):
        """清空面板"""
        self.messages = []
        self.messages_table.setRowCount(0)
        self.detail_text.clear()


class WelcomePanel(QWidget):
    """欢迎面板 - Clash Verge 风格"""
    
    add_connection_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        
        # Logo/标题
        title = QLabel("🎯 Kafka Explorer")
        title.setStyleSheet("""
            QLabel {
                font-size: 48px;
                font-weight: bold;
                color: #5b9cf4;
                background-color: transparent;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("轻量级 Kafka 集群管理工具")
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 15px; 
                color: #9ca3af; 
                background-color: transparent;
                letter-spacing: 1px;
            }
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        # 功能卡片容器
        features = QHBoxLayout()
        features.setSpacing(20)
        features.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 定义卡片数据和对应的强调色
        cards_data = [
            ("📋", "Topic 管理", "浏览和管理 Topics", "#3d5afe"),
            ("👥", "消费者组", "监控 Consumer Groups", "#4caf50"),
            ("📨", "消息浏览", "查看和发送消息", "#ff9800"),
        ]
        
        for icon, card_title, desc, accent_color in cards_data:
            card = QFrame()
            card.setObjectName("featureCard")
            card.setProperty("accentColor", accent_color)
            card.setFixedSize(200, 160)
            
            card_layout = QVBoxLayout(card)
            card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.setSpacing(8)
            card_layout.setContentsMargins(16, 20, 16, 20)
            
            # 图标容器 - 带背景色
            icon_container = QLabel(icon)
            icon_container.setStyleSheet(f"""
                QLabel {{
                    font-size: 32px;
                    background-color: {accent_color};
                    border-radius: 10px;
                    padding: 8px;
                }}
            """)
            icon_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_container.setFixedSize(56, 56)
            card_layout.addWidget(icon_container, alignment=Qt.AlignmentFlag.AlignCenter)
            
            title_label = QLabel(card_title)
            title_label.setObjectName("featureCardTitle")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(title_label)
            
            desc_label = QLabel(desc)
            desc_label.setObjectName("featureCardDesc")
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(desc_label)
            
            features.addWidget(card)
        
        layout.addLayout(features)
        
        # 添加连接按钮
        layout.addSpacing(32)
        
        add_btn = QPushButton("➕ 添加 Kafka 连接")
        add_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: 600;
                padding: 14px 36px;
                background-color: #3d5afe;
                color: #ffffff;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #5b9cf4;
            }
            QPushButton:pressed {
                background-color: #2196f3;
            }
        """)
        add_btn.clicked.connect(self.add_connection_clicked.emit)
        layout.addWidget(add_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 版本信息
        version_label = QLabel("v1.0.0")
        version_label.setStyleSheet("""
            QLabel {
                font-size: 11px; 
                color: #565f89; 
                background-color: transparent;
            }
        """)
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)

