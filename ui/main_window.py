"""主窗口"""

import json
import os
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, List


def get_app_dir() -> Path:
    """获取应用程序目录（支持打包后的exe和直接运行）"""
    if getattr(sys, 'frozen', False):
        # 打包成 exe 后
        return Path(sys.executable).parent
    else:
        # 直接运行 Python 脚本
        return Path(__file__).parent.parent


def get_resources_dir() -> Path:
    """获取 resources 目录（样式表图片等），兼容打包单文件/目录模式"""
    if getattr(sys, 'frozen', False):
        base = Path(getattr(sys, '_MEIPASS', str(Path(sys.executable).parent)))
        return (base / "resources").resolve()
    return (Path(__file__).parent.parent / "resources").resolve()

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTreeWidget, QTreeWidgetItem, QStackedWidget,
    QToolBar, QStatusBar, QMessageBox, QMenu, QApplication,
    QLabel, QProgressDialog, QLineEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSettings, QSize
from PyQt6.QtGui import QAction, QIcon, QFont

from kafka_client import KafkaClusterClient, ClusterConnection
from kafka_client.models import TopicInfo, ConsumerGroupInfo, KafkaMessage

from .dialogs import (
    ConnectionDialog, CreateTopicDialog, AddPartitionsDialog,
    ResetOffsetDialog, CreateConsumerGroupDialog, ConsumeMessagesDialog,
    MessageProducerDialog,
)
from .panels import (
    TopicDetailPanel, ConsumerGroupPanel, MessageBrowserPanel,
    WelcomePanel, LoadingOverlay
)
from .styles import THEMES

logger = logging.getLogger(__name__)


class WorkerThread(QThread):
    """后台工作线程"""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self._stop_requested = False
    
    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            if not self._stop_requested:
                self.finished.emit(result)
        except Exception as e:
            if not self._stop_requested:
                logger.exception("Worker thread error")
                self.error.emit(str(e))
    
    def stop(self):
        """请求停止线程"""
        self._stop_requested = True
        if self.isRunning():
            self.terminate()
            self.wait(3000)  # 等待最多3秒


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        
        self.connections: Dict[str, ClusterConnection] = {}
        self.clients: Dict[str, KafkaClusterClient] = {}
        self.current_client: Optional[KafkaClusterClient] = None
        self.current_connection_name: Optional[str] = None
        
        # 跟踪所有活动线程
        self.active_threads: List[WorkerThread] = []
        
        self.settings = QSettings("KafkaExplorer", "KafkaExplorer")
        # 配置文件放在程序运行目录
        self.config_path = get_app_dir() / "config" / "connections.json"
        
        self.setup_ui()
        self.load_connections()
        self.restore_state()
    
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("Kafka Explorer")
        self.setMinimumSize(1200, 800)
        
        # 设置应用图标
        from resources import create_kafka_icon
        self.setWindowIcon(create_kafka_icon())
        
        # 应用主题
        self.current_theme = self.settings.value("theme", "dark")
        self.apply_theme(self.current_theme)
        
        # 创建菜单栏
        self.create_menus()
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧导航面板
        left_panel = QWidget()
        left_panel.setObjectName("leftPanel")
        left_panel.setMinimumWidth(280)
        left_panel.setMaximumWidth(400)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(8, 8, 8, 8)
        left_layout.setSpacing(8)
        
        # 搜索框
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍 搜索 Topic...")
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.textChanged.connect(self.filter_topics)
        left_layout.addWidget(self.search_edit)
        
        # 导航树
        self.nav_tree = QTreeWidget()
        self.nav_tree.setHeaderHidden(True)
        self.nav_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.nav_tree.customContextMenuRequested.connect(self.show_tree_menu)
        self.nav_tree.itemClicked.connect(self.on_tree_item_clicked)
        self.nav_tree.itemDoubleClicked.connect(self.on_tree_item_double_clicked)
        left_layout.addWidget(self.nav_tree)
        
        splitter.addWidget(left_panel)
        
        # 右侧内容区
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(16, 16, 16, 16)
        
        # 堆叠窗口
        self.content_stack = QStackedWidget()
        right_layout.addWidget(self.content_stack)
        
        # 欢迎面板
        self.welcome_panel = WelcomePanel()
        self.welcome_panel.add_connection_clicked.connect(self.add_connection)
        self.content_stack.addWidget(self.welcome_panel)
        
        # Topic详情面板
        self.topic_panel = TopicDetailPanel()
        self.topic_panel.refresh_btn.clicked.connect(self.refresh_current_topic)
        self.topic_panel.message_browse_requested.connect(self.browse_topic_messages)
        self.topic_panel.send_message_requested.connect(self.show_producer_dialog)
        self.topic_panel.add_partitions_requested.connect(self.on_add_partitions_from_panel)
        self.content_stack.addWidget(self.topic_panel)
        
        # Consumer Group面板
        self.consumer_panel = ConsumerGroupPanel()
        self.consumer_panel.refresh_btn.clicked.connect(self.refresh_current_group)
        self.consumer_panel.reset_offsets_requested.connect(self.on_reset_offsets_requested)
        self.content_stack.addWidget(self.consumer_panel)
        
        # 消息浏览器面板
        self.message_panel = MessageBrowserPanel()
        self.message_panel.refresh_requested.connect(self.fetch_messages)
        self.message_panel.resend_message_requested.connect(self.resend_message)
        self.message_panel.check_consumption_requested.connect(self.check_message_consumption)
        self.content_stack.addWidget(self.message_panel)
        
        splitter.addWidget(right_container)
        splitter.setSizes([300, 900])
        
        # 加载遮罩
        self.loading_overlay = LoadingOverlay(self)
        self.loading_overlay.apply_theme(self.current_theme)
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
        
        # 状态栏连接状态
        self.connection_label = QLabel("未连接")
        self.connection_label.setStyleSheet("color: #9ca3af; padding: 0 16px;")
        self.status_bar.addPermanentWidget(self.connection_label)
    
    def create_menus(self):
        """创建菜单"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        
        add_conn_action = QAction("添加连接(&A)", self)
        add_conn_action.setShortcut("Ctrl+N")
        add_conn_action.triggered.connect(self.add_connection)
        file_menu.addAction(add_conn_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 视图菜单
        view_menu = menubar.addMenu("视图(&V)")
        
        refresh_action = QAction("刷新(&R)", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_current)
        view_menu.addAction(refresh_action)
        
        view_menu.addSeparator()
        
        # 主题子菜单
        theme_menu = view_menu.addMenu("🎨 主题")
        
        self.dark_theme_action = QAction("🌙 暗色主题", self)
        self.dark_theme_action.setCheckable(True)
        self.dark_theme_action.triggered.connect(lambda: self.switch_theme('dark'))
        theme_menu.addAction(self.dark_theme_action)
        
        self.light_theme_action = QAction("☀️ 亮色主题", self)
        self.light_theme_action.setCheckable(True)
        self.light_theme_action.triggered.connect(lambda: self.switch_theme('light'))
        theme_menu.addAction(self.light_theme_action)
        
        # 更新主题菜单选中状态
        self.update_theme_menu()
        
        # 工具菜单
        tools_menu = menubar.addMenu("工具(&T)")
        
        consume_action = QAction("消费消息(&C)", self)
        consume_action.triggered.connect(self.show_consume_messages_dialog)
        tools_menu.addAction(consume_action)
        
        producer_action = QAction("发送消息(&S)", self)
        producer_action.setShortcut("Ctrl+P")
        producer_action.triggered.connect(self.show_producer_dialog)
        tools_menu.addAction(producer_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        
        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """创建工具栏"""
        # 不创建工具栏按钮，功能通过菜单和右键菜单访问
        pass
    
    def load_connections(self):
        """从配置文件加载连接"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for conn_data in data:
                        conn = ClusterConnection.from_dict(conn_data)
                        self.connections[conn.name] = conn
                        self.add_connection_to_tree(conn)
            except Exception as e:
                logger.error(f"加载连接配置失败: {e}")
    
    def save_connections(self):
        """保存连接到配置文件"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            data = [conn.to_dict() for conn in self.connections.values()]
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存连接配置失败: {e}")
    
    def add_connection_to_tree(self, conn: ClusterConnection):
        """添加连接到导航树"""
        item = QTreeWidgetItem(self.nav_tree)
        item.setText(0, f"📡 {conn.name}")
        item.setData(0, Qt.ItemDataRole.UserRole, {"type": "connection", "name": conn.name})
        
        # 添加子节点占位
        topics_item = QTreeWidgetItem(item)
        topics_item.setText(0, "📋 Topics")
        topics_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "topics_folder", "connection": conn.name})
        
        groups_item = QTreeWidgetItem(item)
        groups_item.setText(0, "👥 Consumer Groups")
        groups_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "groups_folder", "connection": conn.name})
    
    def add_connection(self):
        """添加新连接"""
        dialog = ConnectionDialog(self)
        if dialog.exec():
            conn = dialog.get_connection()
            self.connections[conn.name] = conn
            self.add_connection_to_tree(conn)
            self.save_connections()
            self.status_bar.showMessage(f"已添加连接: {conn.name}", 3000)
    
    def edit_connection(self, name: str):
        """编辑连接"""
        if name not in self.connections:
            return
        
        conn = self.connections[name]
        dialog = ConnectionDialog(self, conn)
        if dialog.exec():
            new_conn = dialog.get_connection()
            
            # 如果名称改变，需要更新
            if new_conn.name != name:
                del self.connections[name]
                if name in self.clients:
                    self.clients[name].disconnect()
                    del self.clients[name]
            
            self.connections[new_conn.name] = new_conn
            self.save_connections()
            self.refresh_tree()
    
    def delete_connection(self, name: str):
        """删除连接"""
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除连接 '{name}' 吗?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if name in self.clients:
                self.clients[name].disconnect()
                del self.clients[name]
            
            if name in self.connections:
                del self.connections[name]
            
            self.save_connections()
            self.refresh_tree()
    
    def connect_to_cluster(self, name: str):
        """连接到集群"""
        if name not in self.connections:
            return
        
        if name in self.clients and self.clients[name].is_connected:
            return
        
        conn = self.connections[name]
        client = KafkaClusterClient(conn)
        
        self.loading_overlay.show_loading(f"正在连接到 {name}...")
        
        def do_connect():
            client.connect()
            return client
        
        def on_finished(client):
            if self.worker in self.active_threads:
                self.active_threads.remove(self.worker)
            self.on_connected(name, client)
        
        def on_error(error):
            if self.worker in self.active_threads:
                self.active_threads.remove(self.worker)
            self.on_connect_error(name, error)
        
        self.worker = WorkerThread(do_connect)
        self.worker.finished.connect(on_finished)
        self.worker.error.connect(on_error)
        self.active_threads.append(self.worker)
        self.worker.start()
    
    def on_connected(self, name: str, client: KafkaClusterClient):
        """连接成功回调"""
        self.loading_overlay.hide_loading()
        self.clients[name] = client
        self.current_client = client
        self.current_connection_name = name
        
        self.connection_label.setText(f"✅ 已连接: {name}")
        self.connection_label.setStyleSheet("color: #4caf50; padding: 0 16px; font-weight: 500;")
        self.status_bar.showMessage(f"已连接到 {name}", 3000)
        
        # 更新树状态显示为已连接
        self.update_connection_tree_status(name, connected=True)
        
        # 加载Topics和Consumer Groups
        self.load_cluster_data(name)
    
    def on_connect_error(self, name: str, error: str):
        """连接失败回调"""
        self.loading_overlay.hide_loading()
        # 确保线程已清理
        if self.worker in self.active_threads:
            self.active_threads.remove(self.worker)
        if self.worker.isRunning():
            self.worker.wait(1000)  # 等待线程结束
        QMessageBox.critical(self, "连接失败", f"无法连接到 {name}:\n{error}")
    
    def load_cluster_data(self, name: str):
        """加载集群数据"""
        if name not in self.clients:
            return
        
        client = self.clients[name]
        
        # 找到对应的树节点
        for i in range(self.nav_tree.topLevelItemCount()):
            item = self.nav_tree.topLevelItem(i)
            data = item.data(0, Qt.ItemDataRole.UserRole)
            if data and data.get("name") == name:
                self.update_cluster_tree(item, client)
                break
    
    def update_cluster_tree(self, cluster_item: QTreeWidgetItem, client: KafkaClusterClient):
        """更新集群树节点（轻量级，只加载名称列表）"""
        # 清空现有子节点
        for i in range(cluster_item.childCount() - 1, -1, -1):
            cluster_item.removeChild(cluster_item.child(i))
        
        name = cluster_item.data(0, Qt.ItemDataRole.UserRole).get("name")
        
        def load_names():
            # 只加载名称，不加载详细数据
            topic_names = client.get_topic_names()
            group_names = client.get_consumer_group_names()
            return topic_names, group_names
        
        self.loading_overlay.show_loading("正在加载列表...")
        
        def on_finished(result):
            if self.worker in self.active_threads:
                self.active_threads.remove(self.worker)
            self.on_names_loaded(cluster_item, name, result)
        
        def on_error(e):
            if self.worker in self.active_threads:
                self.active_threads.remove(self.worker)
            self.on_data_load_error(e)
        
        self.worker = WorkerThread(load_names)
        self.worker.finished.connect(on_finished)
        self.worker.error.connect(on_error)
        self.active_threads.append(self.worker)
        self.worker.start()
    
    def on_names_loaded(self, cluster_item: QTreeWidgetItem, name: str, result):
        """名称列表加载完成"""
        self.loading_overlay.hide_loading()
        topic_names, group_names = result
        
        # Topics文件夹
        topics_item = QTreeWidgetItem(cluster_item)
        topics_item.setText(0, f"📋 Topics ({len(topic_names)})")
        topics_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "topics_folder", "connection": name})
        
        for topic_name in topic_names:
            topic_item = QTreeWidgetItem(topics_item)
            icon = "🔒" if topic_name.startswith('__') else "📄"
            topic_item.setText(0, f"{icon} {topic_name}")
            topic_item.setData(0, Qt.ItemDataRole.UserRole, {
                "type": "topic",
                "connection": name,
                "topic": topic_name
            })
        
        # Consumer Groups文件夹
        groups_item = QTreeWidgetItem(cluster_item)
        groups_item.setText(0, f"👥 Consumer Groups ({len(group_names)})")
        groups_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "groups_folder", "connection": name})
        
        for group_id, protocol_type in group_names:
            group_item = QTreeWidgetItem(groups_item)
            # 名称列表模式下不获取状态，使用默认图标
            group_item.setText(0, f"👤 {group_id}")
            group_item.setData(0, Qt.ItemDataRole.UserRole, {
                "type": "consumer_group",
                "connection": name,
                "group": group_id
            })
        
        cluster_item.setExpanded(True)
        topics_item.setExpanded(True)  # 展开 Topics，便于看到 Topic 列表（如增加分区后）
    
    def on_data_load_error(self, error: str):
        """数据加载失败"""
        self.loading_overlay.hide_loading()
        QMessageBox.warning(self, "加载失败", f"无法加载集群数据:\n{error}")
    
    def show_tree_menu(self, pos):
        """显示树节点右键菜单"""
        item = self.nav_tree.itemAt(pos)
        
        # 空白区域右键 - 显示添加连接菜单
        if not item:
            menu = QMenu(self)
            add_action = menu.addAction("➕ 添加连接")
            add_action.triggered.connect(self.add_connection)
            menu.exec(self.nav_tree.mapToGlobal(pos))
            return
        
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return
        
        menu = QMenu(self)
        
        if data["type"] == "connection":
            name = data["name"]
            
            connect_action = menu.addAction("连接")
            connect_action.triggered.connect(lambda: self.connect_to_cluster(name))
            
            disconnect_action = menu.addAction("断开连接")
            disconnect_action.triggered.connect(lambda: self.disconnect_from_cluster(name))
            
            menu.addSeparator()
            
            edit_action = menu.addAction("编辑")
            edit_action.triggered.connect(lambda: self.edit_connection(name))
            
            delete_action = menu.addAction("删除")
            delete_action.triggered.connect(lambda: self.delete_connection(name))
        
        elif data["type"] == "topics_folder":
            refresh_action = menu.addAction("刷新")
            refresh_action.triggered.connect(lambda: self.refresh_topics(data["connection"]))
            
            menu.addSeparator()
            
            create_action = menu.addAction("创建 Topic")
            create_action.triggered.connect(lambda: self.create_topic(data["connection"]))
        
        elif data["type"] == "topic":
            browse_action = menu.addAction("浏览消息")
            browse_action.triggered.connect(lambda: self.browse_topic_messages(data["topic"], -1))
            
            send_action = menu.addAction("发送消息")
            send_action.triggered.connect(lambda: self.show_producer_dialog(data["topic"]))
            
            add_partitions_action = menu.addAction("增加分区")
            add_partitions_action.triggered.connect(
                lambda: self.add_partitions(data["connection"], data["topic"], current_count=None)
            )
            
            menu.addSeparator()
            
            copy_action = menu.addAction("复制 Topic 名称")
            copy_action.triggered.connect(lambda: self.copy_topic_name(data["topic"]))
            
            menu.addSeparator()
            
            delete_action = menu.addAction("删除 Topic")
            delete_action.triggered.connect(lambda: self.delete_topic(data["connection"], data["topic"]))
        
        elif data["type"] == "groups_folder":
            create_action = menu.addAction("创建消费者组")
            create_action.triggered.connect(lambda: self.create_consumer_group(data["connection"]))
            menu.addSeparator()
            refresh_action = menu.addAction("刷新")
            refresh_action.triggered.connect(lambda: self.refresh_groups(data["connection"]))
        
        menu.exec(self.nav_tree.mapToGlobal(pos))
    
    def on_tree_item_clicked(self, item: QTreeWidgetItem, column: int):
        """树节点单击事件"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return
        
        if data["type"] == "topic":
            self.show_topic_detail(data["connection"], data["topic"])
        
        elif data["type"] == "consumer_group":
            self.show_consumer_group_detail(data["connection"], data["group"])
    
    def on_tree_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """树节点双击事件"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return
        
        if data["type"] == "connection":
            self.connect_to_cluster(data["name"])
    
    def show_topic_detail(self, connection: str, topic_name: str):
        """显示Topic详情"""
        if connection not in self.clients:
            self.connect_to_cluster(connection)
            return
        
        client = self.clients[connection]
        self.current_client = client
        self.current_connection_name = connection
        
        self.loading_overlay.show_loading("正在加载Topic信息...")
        
        def on_finished(topic):
            if self.worker in self.active_threads:
                self.active_threads.remove(self.worker)
            self.on_topic_loaded(topic)
        
        def on_error(e):
            if self.worker in self.active_threads:
                self.active_threads.remove(self.worker)
            self.on_load_error("Topic", e)
        
        self.worker = WorkerThread(client.get_topic_detail, topic_name)
        self.worker.finished.connect(on_finished)
        self.worker.error.connect(on_error)
        self.active_threads.append(self.worker)
        self.worker.start()
    
    def on_topic_loaded(self, topic: TopicInfo):
        """Topic加载完成"""
        self.loading_overlay.hide_loading()
        if topic:
            self.topic_panel.load_topic(topic)
            self.content_stack.setCurrentWidget(self.topic_panel)
    
    def show_consumer_group_detail(self, connection: str, group_id: str):
        """显示消费者组详情"""
        if connection not in self.clients:
            self.connect_to_cluster(connection)
            return
        
        client = self.clients[connection]
        self.current_client = client
        self.current_connection_name = connection
        
        self.loading_overlay.show_loading("正在加载消费者组信息...")
        
        def on_finished(group):
            if self.worker in self.active_threads:
                self.active_threads.remove(self.worker)
            self.on_group_loaded(group)
        
        def on_error(e):
            if self.worker in self.active_threads:
                self.active_threads.remove(self.worker)
            self.on_load_error("消费者组", e)
        
        self.worker = WorkerThread(client.get_consumer_group_detail, group_id)
        self.worker.finished.connect(on_finished)
        self.worker.error.connect(on_error)
        self.active_threads.append(self.worker)
        self.worker.start()
    
    def on_group_loaded(self, group: ConsumerGroupInfo):
        """消费者组加载完成"""
        self.loading_overlay.hide_loading()
        if group:
            self.consumer_panel.load_group(group)
            self.content_stack.setCurrentWidget(self.consumer_panel)

    def on_reset_offsets_requested(self):
        """重置消费点：弹窗选择目标与范围，然后调用客户端重置并刷新组详情"""
        if not self.current_connection_name or not self.current_client:
            QMessageBox.warning(self, "警告", "请先连接到 Kafka 集群")
            return
        group = self.consumer_panel.current_group
        if not group:
            QMessageBox.warning(self, "警告", "请先选择要操作的消费者组")
            return
        selected = self.consumer_panel.get_selected_offset_partitions()
        dialog = ResetOffsetDialog(
            self,
            group_id=group.group_id,
            has_selection=bool(selected),
            partition_count=len(group.offsets),
        )
        if not dialog.exec():
            return
        target = dialog.get_target()
        scope = dialog.get_scope()
        if scope == "all":
            topic_partitions = [(o.topic, o.partition) for o in group.offsets]
        else:
            topic_partitions = selected
            if not topic_partitions:
                QMessageBox.warning(self, "警告", "请先在 Offset 表格中选中要重置的分区")
                return
        self.loading_overlay.show_loading("正在重置消费点...")

        def do_reset():
            self.current_client.reset_consumer_group_offsets(group.group_id, topic_partitions, target)

        def on_finished(_):
            if self.worker in self.active_threads:
                self.active_threads.remove(self.worker)
            self.loading_overlay.hide_loading()
            QMessageBox.information(self, "成功", f"已将该组 {len(topic_partitions)} 个分区重置到「{target}」")
            self.show_consumer_group_detail(self.current_connection_name, group.group_id)

        def on_error(e):
            if self.worker in self.active_threads:
                self.active_threads.remove(self.worker)
            self.loading_overlay.hide_loading()
            QMessageBox.critical(self, "错误", f"重置消费点失败:\n{e}")

        self.worker = WorkerThread(do_reset)
        self.worker.finished.connect(on_finished)
        self.worker.error.connect(on_error)
        self.active_threads.append(self.worker)
        self.worker.start()

    def on_load_error(self, type_name: str, error: str):
        """加载错误处理"""
        self.loading_overlay.hide_loading()
        QMessageBox.warning(self, "加载失败", f"无法加载{type_name}信息:\n{error}")
    
    def browse_topic_messages(self, topic: str, partition: int):
        """浏览Topic消息"""
        self.message_panel.set_topic(topic, partition)
        self.content_stack.setCurrentWidget(self.message_panel)
        
        # 自动获取消息
        if self.current_client:
            self.fetch_messages(topic, partition, -1, 100)

    def show_consume_messages_dialog(self):
        """消费消息：拉取 Topic/消费者组列表后弹窗，确定后打开消息浏览器并拉取。"""
        if not self.current_client or not self.current_connection_name:
            QMessageBox.warning(self, "警告", "请先连接到 Kafka 集群")
            return
        client = self.current_client
        self.loading_overlay.show_loading("正在加载 Topic 与消费者组列表...")

        def load_data():
            topics = client.get_topic_names()
            groups = client.get_consumer_group_names()
            return topics, [g[0] for g in groups]

        def on_loaded(result):
            if self.worker in self.active_threads:
                self.active_threads.remove(self.worker)
            self.loading_overlay.hide_loading()
            topic_names, group_names = result
            dialog = ConsumeMessagesDialog(self, topic_names=topic_names, group_names=group_names)
            if not dialog.exec():
                return
            topic = dialog.get_topic()
            partition = dialog.get_partition()
            group_id = dialog.get_group_id()
            self.message_panel.set_topic(topic, partition)
            self.content_stack.setCurrentWidget(self.message_panel)
            self.fetch_messages(topic, partition, -1, 100, from_beginning=False, sort_field="offset", group_id=group_id)

        def on_error(e):
            if self.worker in self.active_threads:
                self.active_threads.remove(self.worker)
            self.loading_overlay.hide_loading()
            QMessageBox.warning(self, "错误", f"加载列表失败:\n{e}")

        self.worker = WorkerThread(load_data)
        self.worker.finished.connect(on_loaded)
        self.worker.error.connect(on_error)
        self.active_threads.append(self.worker)
        self.worker.start()

    def fetch_messages(self, topic: str, partition: int, offset: int, limit: int, from_beginning: bool = False, sort_field: str = "offset", group_id: Optional[str] = None):
        """获取消息。group_id 不为空时从该消费者组的提交位点开始拉取。"""
        if not self.current_client:
            QMessageBox.warning(self, "警告", "请先连接到Kafka集群")
            return
        
        self.loading_overlay.show_loading("正在获取消息...")
        
        part = partition if partition >= 0 else None
        off = offset if offset >= 0 else None
        
        def on_finished(messages):
            if self.worker in self.active_threads:
                self.active_threads.remove(self.worker)
            self.on_messages_loaded(messages)
        
        def on_error(e):
            if self.worker in self.active_threads:
                self.active_threads.remove(self.worker)
            self.on_load_error("消息", e)
        
        self.worker = WorkerThread(
            self.current_client.consume_messages,
            topic, part, off, limit, from_beginning=from_beginning, sort_field=sort_field, group_id=group_id
        )
        self.worker.finished.connect(on_finished)
        self.worker.error.connect(on_error)
        self.active_threads.append(self.worker)
        self.worker.start()
    
    def on_messages_loaded(self, messages: List[KafkaMessage]):
        """消息加载完成"""
        self.loading_overlay.hide_loading()
        self.message_panel.load_messages(messages)
        self.status_bar.showMessage(f"已加载 {len(messages)} 条消息", 3000)
    
    def show_producer_dialog(self, topic=None):
        """显示消息发送对话框"""
        # 处理 PyQt 信号传递的 bool 参数
        if topic is None or isinstance(topic, bool):
            topic = ""
        
        if not self.current_client:
            QMessageBox.warning(self, "警告", "请先连接到Kafka集群")
            return
        
        dialog = MessageProducerDialog(self, topic)
        if dialog.exec():
            data = dialog.get_message_data()
            
            try:
                value = data['value'].encode('utf-8')
                key = data['key'].encode('utf-8') if data['key'] else None
                
                self.current_client.produce_message(
                    topic=data['topic'],
                    value=value,
                    key=key,
                    partition=data['partition']
                )
                QMessageBox.information(self, "成功", "消息发送成功！")
                # 若当前正在查看该 Topic 详情，重新加载以更新消息总数和分区信息
                sent_topic = data['topic']
                if (self.current_connection_name
                        and self.topic_panel.current_topic
                        and self.topic_panel.current_topic.name == sent_topic):
                    self.show_topic_detail(self.current_connection_name, sent_topic)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"消息发送失败:\n{str(e)}")
    
    def resend_message(self, topic: str, key, value, headers):
        """重新发送消息"""
        if not self.current_client:
            QMessageBox.warning(self, "警告", "请先连接到Kafka集群")
            return
        
        try:
            self.current_client.produce_message(
                topic=topic,
                value=value,
                key=key,
                headers=headers
            )
            QMessageBox.information(self, "成功", f"消息已重新发送到 {topic}")
            # 刷新消息列表
            self.message_panel.on_fetch_clicked()
            # 若当前正在查看该 Topic 详情，重新加载以更新消息总数
            if (self.current_connection_name
                    and self.topic_panel.current_topic
                    and self.topic_panel.current_topic.name == topic):
                self.show_topic_detail(self.current_connection_name, topic)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"消息发送失败:\n{str(e)}")
    
    def check_message_consumption(self, topic: str, partition: int, offset: int, callback):
        """检查消息消费状态"""
        if not self.current_client:
            callback([])
            return
        
        def do_check():
            return self.current_client.get_message_consumption_status(topic, partition, offset)
        
        def on_finished(result):
            if worker in self.active_threads:
                self.active_threads.remove(worker)
            callback(result)
        
        def on_error(e):
            if worker in self.active_threads:
                self.active_threads.remove(worker)
            callback([])
        
        worker = WorkerThread(do_check)
        worker.finished.connect(on_finished)
        worker.error.connect(on_error)
        self.active_threads.append(worker)
        worker.start()
        # 保持引用防止被回收
        self._consumption_check_worker = worker
    
    def on_add_partitions_from_panel(self, topic_name: str, current_count: int):
        """从 Topic 详情面板发起增加分区"""
        if not self.current_connection_name:
            QMessageBox.warning(self, "警告", "请先连接到集群")
            return
        self.add_partitions(self.current_connection_name, topic_name, current_count=current_count)
    
    def add_partitions(self, connection: str, topic_name: str, current_count: Optional[int] = None):
        """增加 Topic 分区数。current_count 为 None 时先异步加载 Topic 详情再弹窗。"""
        if connection not in self.clients:
            QMessageBox.warning(self, "警告", "请先连接到集群")
            return
        
        def do_show_dialog_and_apply(topic_info: Optional[TopicInfo]):
            self.loading_overlay.hide_loading()
            if self.worker in self.active_threads:
                self.active_threads.remove(self.worker)
            if not topic_info:
                QMessageBox.warning(self, "错误", "无法获取 Topic 信息")
                return
            cnt = topic_info.partition_count
            dialog = AddPartitionsDialog(self, topic_info.name, cnt)
            if not dialog.exec():
                return
            new_total = dialog.get_new_total_partitions()
            try:
                self.clients[connection].create_partitions(topic_info.name, new_total)
                QMessageBox.information(
                    self, "成功",
                    f"Topic '{topic_info.name}' 分区数已从 {cnt} 调整为 {new_total}。"
                )
                self.refresh_topics(connection)
                if (self.current_connection_name == connection
                        and self.topic_panel.current_topic
                        and self.topic_panel.current_topic.name == topic_info.name):
                    self.show_topic_detail(connection, topic_info.name)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"增加分区失败:\n{str(e)}")
        
        if current_count is not None:
            dialog = AddPartitionsDialog(self, topic_name, current_count)
            if not dialog.exec():
                return
            new_total = dialog.get_new_total_partitions()
            try:
                self.clients[connection].create_partitions(topic_name, new_total)
                QMessageBox.information(
                    self, "成功",
                    f"Topic '{topic_name}' 分区数已从 {current_count} 调整为 {new_total}。"
                )
                self.refresh_topics(connection)
                if (self.current_connection_name == connection
                        and self.topic_panel.current_topic
                        and self.topic_panel.current_topic.name == topic_name):
                    self.show_topic_detail(connection, topic_name)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"增加分区失败:\n{str(e)}")
            return
        
        self.loading_overlay.show_loading("正在获取 Topic 信息...")
        
        def on_error(e):
            if self.worker in self.active_threads:
                self.active_threads.remove(self.worker)
            self.loading_overlay.hide_loading()
            QMessageBox.warning(self, "错误", f"无法获取 Topic 信息:\n{e}")
        
        self.worker = WorkerThread(self.clients[connection].get_topic_detail, topic_name)
        self.worker.finished.connect(do_show_dialog_and_apply)
        self.worker.error.connect(on_error)
        self.active_threads.append(self.worker)
        self.worker.start()
    
    def create_topic(self, connection: str):
        """创建Topic"""
        if connection not in self.clients:
            QMessageBox.warning(self, "警告", "请先连接到集群")
            return
        
        dialog = CreateTopicDialog(self)
        if dialog.exec():
            config = dialog.get_topic_config()
            
            try:
                self.clients[connection].create_topic(
                    topic_name=config['name'],
                    num_partitions=config['partitions'],
                    replication_factor=config['replication_factor']
                )
                QMessageBox.information(self, "成功", f"Topic '{config['name']}' 创建成功！")
                self.refresh_topics(connection)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"Topic创建失败:\n{str(e)}")

    def create_consumer_group(self, connection: str):
        """创建消费者组：先拉取 Topic 列表，弹窗填写组 ID 与订阅 Topic，再调用客户端创建并刷新列表。"""
        if connection not in self.clients:
            QMessageBox.warning(self, "警告", "请先连接到集群")
            return
        client = self.clients[connection]
        self.loading_overlay.show_loading("正在获取 Topic 列表...")

        def on_topic_names_loaded(topic_names):
            if self.worker in self.active_threads:
                self.active_threads.remove(self.worker)
            self.loading_overlay.hide_loading()
            dialog = CreateConsumerGroupDialog(self, topic_names=topic_names)
            if not dialog.exec():
                return
            group_id = dialog.get_group_id()
            topics = dialog.get_selected_topics()
            target = dialog.get_target()
            self.loading_overlay.show_loading("正在创建消费者组...")

            def do_create():
                client.create_consumer_group(group_id, topics, target)

            def on_created(_):
                if self.worker in self.active_threads:
                    self.active_threads.remove(self.worker)
                self.loading_overlay.hide_loading()
                QMessageBox.information(
                    self, "成功",
                    f"消费者组「{group_id}」已创建，已订阅 {len(topics)} 个 Topic，初始消费点: {target}。"
                )
                self.refresh_groups(connection)

            def on_create_error(e):
                if self.worker in self.active_threads:
                    self.active_threads.remove(self.worker)
                self.loading_overlay.hide_loading()
                QMessageBox.critical(self, "错误", f"创建消费者组失败:\n{e}")

            self.worker = WorkerThread(do_create)
            self.worker.finished.connect(on_created)
            self.worker.error.connect(on_create_error)
            self.active_threads.append(self.worker)
            self.worker.start()

        def on_error(e):
            if self.worker in self.active_threads:
                self.active_threads.remove(self.worker)
            self.loading_overlay.hide_loading()
            QMessageBox.warning(self, "错误", f"获取 Topic 列表失败:\n{e}")

        self.worker = WorkerThread(client.get_topic_names)
        self.worker.finished.connect(on_topic_names_loaded)
        self.worker.error.connect(on_error)
        self.active_threads.append(self.worker)
        self.worker.start()

    def copy_topic_name(self, topic_name: str):
        """复制Topic名称到剪贴板"""
        clipboard = QApplication.clipboard()
        clipboard.setText(topic_name)
        self.status_bar.showMessage(f"已复制: {topic_name}", 3000)
    
    def delete_topic(self, connection: str, topic_name: str):
        """删除Topic"""
        if connection not in self.clients:
            return
        
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除Topic '{topic_name}' 吗?\n此操作不可撤销！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.clients[connection].delete_topic(topic_name)
                QMessageBox.information(self, "成功", f"Topic '{topic_name}' 已删除")
                self.refresh_topics(connection)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"Topic删除失败:\n{str(e)}")
    
    def disconnect_from_cluster(self, name: str):
        """断开集群连接"""
        if name not in self.clients:
            QMessageBox.information(self, "提示", f"连接 '{name}' 尚未建立连接")
            return
        
        try:
            self.clients[name].disconnect()
            del self.clients[name]
            
            if self.current_connection_name == name:
                self.current_client = None
                self.current_connection_name = None
                self.connection_label.setText("未连接")
                self.connection_label.setStyleSheet("color: #9ca3af; padding: 0 16px;")
            
            # 刷新树状态，更新连接节点的显示
            self.update_connection_tree_status(name, connected=False)
            
            self.status_bar.showMessage(f"已断开连接: {name}", 3000)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"断开连接失败:\n{str(e)}")
    
    def update_connection_tree_status(self, name: str, connected: bool):
        """更新连接在树中的显示状态"""
        for i in range(self.nav_tree.topLevelItemCount()):
            item = self.nav_tree.topLevelItem(i)
            data = item.data(0, Qt.ItemDataRole.UserRole)
            if data and data.get("name") == name:
                if connected:
                    item.setText(0, f"🟢 {name}")
                else:
                    item.setText(0, f"📡 {name}")
                    # 清空子节点内容（保留文件夹节点但移除 topic 和 group 列表）
                    for j in range(item.childCount()):
                        child = item.child(j)
                        while child.childCount() > 0:
                            child.removeChild(child.child(0))
                    # 收起节点
                    item.setExpanded(False)
                break
    
    def refresh_tree(self):
        """刷新导航树"""
        self.nav_tree.clear()
        for conn in self.connections.values():
            self.add_connection_to_tree(conn)
    
    def filter_topics(self, search_text: str):
        """过滤 Topic 列表"""
        search_text = search_text.lower().strip()
        
        # 遍历所有连接节点
        for i in range(self.nav_tree.topLevelItemCount()):
            conn_item = self.nav_tree.topLevelItem(i)
            
            # 遍历连接下的子节点（Topics文件夹、Consumer Groups文件夹）
            for j in range(conn_item.childCount()):
                folder_item = conn_item.child(j)
                folder_data = folder_item.data(0, Qt.ItemDataRole.UserRole)
                
                if folder_data and folder_data.get("type") == "topics_folder":
                    # 过滤 Topics
                    visible_count = 0
                    for k in range(folder_item.childCount()):
                        topic_item = folder_item.child(k)
                        topic_data = topic_item.data(0, Qt.ItemDataRole.UserRole)
                        
                        if topic_data and topic_data.get("type") == "topic":
                            topic_name = topic_data.get("topic", "").lower()
                            
                            if not search_text or search_text in topic_name:
                                topic_item.setHidden(False)
                                visible_count += 1
                            else:
                                topic_item.setHidden(True)
                    
                    # 更新文件夹显示的计数
                    if search_text:
                        folder_item.setText(0, f"📋 Topics ({visible_count} / {folder_item.childCount()})")
                    else:
                        folder_item.setText(0, f"📋 Topics ({folder_item.childCount()})")
                    
                    # 如果有搜索词，自动展开 Topics 文件夹
                    if search_text:
                        folder_item.setExpanded(True)
    
    def refresh_topics(self, connection: str):
        """刷新Topics"""
        if connection in self.clients:
            for i in range(self.nav_tree.topLevelItemCount()):
                item = self.nav_tree.topLevelItem(i)
                data = item.data(0, Qt.ItemDataRole.UserRole)
                if data and data.get("name") == connection:
                    self.update_cluster_tree(item, self.clients[connection])
                    break
    
    def refresh_groups(self, connection: str):
        """刷新Consumer Groups"""
        self.refresh_topics(connection)  # 使用相同的刷新逻辑
    
    def refresh_current(self):
        """刷新当前视图"""
        current = self.content_stack.currentWidget()
        
        if current == self.topic_panel and self.topic_panel.current_topic:
            self.refresh_current_topic()
        elif current == self.consumer_panel and self.consumer_panel.current_group:
            self.refresh_current_group()
    
    def refresh_current_topic(self):
        """刷新当前Topic"""
        if self.topic_panel.current_topic and self.current_client:
            topic_name = self.topic_panel.current_topic.name
            self.show_topic_detail(self.current_connection_name, topic_name)
    
    def refresh_current_group(self):
        """刷新当前消费者组"""
        if self.consumer_panel.current_group and self.current_client:
            group_id = self.consumer_panel.current_group.group_id
            self.show_consumer_group_detail(self.current_connection_name, group_id)
    
    def apply_theme(self, theme_name: str):
        """应用主题"""
        if theme_name in THEMES:
            sheet = THEMES[theme_name]
            # 注入 QSpinBox 箭头图片路径（Qt 样式表 url 需使用正斜杠）
            res_dir = get_resources_dir()
            path_str = str(res_dir).replace("\\", "/")
            sheet = sheet.replace("{{RESOURCES_DIR}}", path_str)
            self.setStyleSheet(sheet)
            self.current_theme = theme_name
            # 更新加载遮罩层的主题
            if hasattr(self, 'loading_overlay'):
                self.loading_overlay.apply_theme(theme_name)
    
    def switch_theme(self, theme_name: str):
        """切换主题"""
        self.apply_theme(theme_name)
        self.settings.setValue("theme", theme_name)
        self.update_theme_menu()
        self.status_bar.showMessage(f"已切换到{'暗色' if theme_name == 'dark' else '亮色'}主题", 3000)
    
    def update_theme_menu(self):
        """更新主题菜单选中状态"""
        self.dark_theme_action.setChecked(self.current_theme == 'dark')
        self.light_theme_action.setChecked(self.current_theme == 'light')
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 Kafka Explorer",
            """<h2>Kafka Explorer</h2>
            <p>版本: 1.0.0</p>
            <p>一个轻量级的 Kafka 集群管理工具</p>
            <p>使用 Python + PyQt6 开发</p>
            """
        )
    
    def restore_state(self):
        """恢复窗口状态"""
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        state = self.settings.value("windowState")
        if state:
            self.restoreState(state)
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 保存窗口状态
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        
        # 停止所有活动线程
        for thread in self.active_threads[:]:  # 使用切片复制列表，避免迭代时修改
            if thread.isRunning():
                thread.stop()
                thread.wait(3000)  # 等待最多3秒
        
        # 断开所有连接
        for client in self.clients.values():
            try:
                client.disconnect()
            except:
                pass
        
        event.accept()
    
    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)
        # 更新遮罩层大小
        self.loading_overlay.setGeometry(self.centralWidget().geometry())

