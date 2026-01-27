"""对话框组件"""

from datetime import datetime

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QPushButton, QLabel, QSpinBox,
    QTextEdit, QGroupBox, QMessageBox, QCheckBox,
    QDialogButtonBox, QTabWidget, QWidget, QFileDialog,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from kafka_client.models import ClusterConnection


class ConnectionDialog(QDialog):
    """连接配置对话框"""
    
    def __init__(self, parent=None, connection: ClusterConnection = None):
        super().__init__(parent)
        self.connection = connection
        self.setup_ui()
        
        if connection:
            self.load_connection(connection)
    
    def setup_ui(self):
        self.setWindowTitle("连接配置" if not self.connection else "编辑连接")
        self.setMinimumWidth(500)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # 标题
        title = QLabel("Kafka 集群连接")
        title.setProperty("heading", True)
        layout.addWidget(title)
        
        # 创建标签页
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # 基本配置标签页
        basic_tab = QWidget()
        basic_layout = QFormLayout(basic_tab)
        basic_layout.setSpacing(12)
        basic_layout.setContentsMargins(16, 16, 16, 16)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("例如: 生产环境集群")
        basic_layout.addRow("连接名称:", self.name_edit)
        
        self.servers_edit = QLineEdit()
        self.servers_edit.setPlaceholderText("例如: localhost:9092,localhost:9093")
        basic_layout.addRow("Bootstrap Servers:", self.servers_edit)
        
        tab_widget.addTab(basic_tab, "基本配置")
        
        # 安全配置标签页
        security_tab = QWidget()
        security_layout = QFormLayout(security_tab)
        security_layout.setSpacing(12)
        security_layout.setContentsMargins(16, 16, 16, 16)
        
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems([
            "PLAINTEXT",
            "SSL",
            "SASL_PLAINTEXT",
            "SASL_SSL"
        ])
        self.protocol_combo.currentTextChanged.connect(self.on_protocol_changed)
        security_layout.addRow("安全协议:", self.protocol_combo)
        
        # SASL配置
        self.sasl_group = QGroupBox("SASL 认证")
        sasl_layout = QFormLayout(self.sasl_group)
        
        self.sasl_mechanism_combo = QComboBox()
        self.sasl_mechanism_combo.addItems(["PLAIN", "SCRAM-SHA-256", "SCRAM-SHA-512", "GSSAPI"])
        self.sasl_mechanism_combo.currentTextChanged.connect(self.on_sasl_mechanism_changed)
        sasl_layout.addRow("机制:", self.sasl_mechanism_combo)
        
        # PLAIN/SCRAM 用户名密码
        self.sasl_username_edit = QLineEdit()
        self.sasl_username_row = sasl_layout.addRow("用户名:", self.sasl_username_edit)
        
        self.sasl_password_edit = QLineEdit()
        self.sasl_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.sasl_password_row = sasl_layout.addRow("密码:", self.sasl_password_edit)
        
        # GSSAPI (Kerberos) 配置
        self.kerberos_service_edit = QLineEdit()
        self.kerberos_service_edit.setPlaceholderText("默认: kafka")
        self.kerberos_service_row = sasl_layout.addRow("Kerberos 服务名:", self.kerberos_service_edit)
        
        self.kerberos_domain_edit = QLineEdit()
        self.kerberos_domain_edit.setPlaceholderText("可选，Kerberos 域名")
        self.kerberos_domain_row = sasl_layout.addRow("Kerberos 域名:", self.kerberos_domain_edit)
        
        # 初始隐藏 Kerberos 配置
        self.kerberos_service_edit.setVisible(False)
        self.kerberos_domain_edit.setVisible(False)
        
        security_layout.addRow(self.sasl_group)
        self.sasl_group.setVisible(False)
        
        # SSL配置
        self.ssl_group = QGroupBox("SSL 配置")
        ssl_layout = QFormLayout(self.ssl_group)
        
        self.ssl_ca_edit = QLineEdit()
        ca_btn = QPushButton("浏览...")
        ca_btn.setProperty("secondary", True)
        ca_btn.clicked.connect(lambda: self.browse_file(self.ssl_ca_edit))
        ca_layout = QHBoxLayout()
        ca_layout.addWidget(self.ssl_ca_edit)
        ca_layout.addWidget(ca_btn)
        ssl_layout.addRow("CA证书:", ca_layout)
        
        self.ssl_cert_edit = QLineEdit()
        cert_btn = QPushButton("浏览...")
        cert_btn.setProperty("secondary", True)
        cert_btn.clicked.connect(lambda: self.browse_file(self.ssl_cert_edit))
        cert_layout = QHBoxLayout()
        cert_layout.addWidget(self.ssl_cert_edit)
        cert_layout.addWidget(cert_btn)
        ssl_layout.addRow("客户端证书:", cert_layout)
        
        self.ssl_key_edit = QLineEdit()
        key_btn = QPushButton("浏览...")
        key_btn.setProperty("secondary", True)
        key_btn.clicked.connect(lambda: self.browse_file(self.ssl_key_edit))
        key_layout = QHBoxLayout()
        key_layout.addWidget(self.ssl_key_edit)
        key_layout.addWidget(key_btn)
        ssl_layout.addRow("客户端私钥:", key_layout)
        
        security_layout.addRow(self.ssl_group)
        self.ssl_group.setVisible(False)
        
        tab_widget.addTab(security_tab, "安全配置")
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        test_btn = QPushButton("测试连接")
        test_btn.setProperty("secondary", True)
        test_btn.clicked.connect(self.test_connection)
        btn_layout.addWidget(test_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setProperty("secondary", True)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_connection)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def on_protocol_changed(self, protocol: str):
        """安全协议变更"""
        is_sasl = "SASL" in protocol
        is_ssl = "SSL" in protocol
        
        self.sasl_group.setVisible(is_sasl)
        self.ssl_group.setVisible(is_ssl)
        
        # 更新 SASL 字段显示
        if is_sasl:
            self.on_sasl_mechanism_changed(self.sasl_mechanism_combo.currentText())
    
    def on_sasl_mechanism_changed(self, mechanism: str):
        """SASL 机制变更"""
        is_gssapi = mechanism == "GSSAPI"
        
        # 用户名密码 - PLAIN/SCRAM 使用
        self.sasl_username_edit.setVisible(not is_gssapi)
        self.sasl_password_edit.setVisible(not is_gssapi)
        
        # 获取 sasl_layout 并更新标签可见性
        sasl_layout = self.sasl_group.layout()
        if sasl_layout:
            # 用户名标签 (row 1)
            username_label = sasl_layout.itemAt(1, QFormLayout.ItemRole.LabelRole)
            if username_label and username_label.widget():
                username_label.widget().setVisible(not is_gssapi)
            # 密码标签 (row 2)
            password_label = sasl_layout.itemAt(2, QFormLayout.ItemRole.LabelRole)
            if password_label and password_label.widget():
                password_label.widget().setVisible(not is_gssapi)
            # Kerberos 服务名标签 (row 3)
            service_label = sasl_layout.itemAt(3, QFormLayout.ItemRole.LabelRole)
            if service_label and service_label.widget():
                service_label.widget().setVisible(is_gssapi)
            # Kerberos 域名标签 (row 4)
            domain_label = sasl_layout.itemAt(4, QFormLayout.ItemRole.LabelRole)
            if domain_label and domain_label.widget():
                domain_label.widget().setVisible(is_gssapi)
        
        # Kerberos 配置 - GSSAPI 使用
        self.kerberos_service_edit.setVisible(is_gssapi)
        self.kerberos_domain_edit.setVisible(is_gssapi)
    
    def browse_file(self, line_edit: QLineEdit):
        """浏览文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择文件", "", "所有文件 (*.*)"
        )
        if file_path:
            line_edit.setText(file_path)
    
    def load_connection(self, conn: ClusterConnection):
        """加载连接配置"""
        self.name_edit.setText(conn.name)
        self.servers_edit.setText(conn.bootstrap_servers)
        self.protocol_combo.setCurrentText(conn.security_protocol)
        
        if conn.sasl_mechanism:
            self.sasl_mechanism_combo.setCurrentText(conn.sasl_mechanism)
        if conn.sasl_username:
            self.sasl_username_edit.setText(conn.sasl_username)
        if conn.sasl_password:
            self.sasl_password_edit.setText(conn.sasl_password)
        # Kerberos 配置
        if conn.sasl_kerberos_service_name:
            self.kerberos_service_edit.setText(conn.sasl_kerberos_service_name)
        if conn.sasl_kerberos_domain_name:
            self.kerberos_domain_edit.setText(conn.sasl_kerberos_domain_name)
        if conn.ssl_cafile:
            self.ssl_ca_edit.setText(conn.ssl_cafile)
        if conn.ssl_certfile:
            self.ssl_cert_edit.setText(conn.ssl_certfile)
        if conn.ssl_keyfile:
            self.ssl_key_edit.setText(conn.ssl_keyfile)
    
    def get_connection(self) -> ClusterConnection:
        """获取连接配置"""
        protocol = self.protocol_combo.currentText()
        is_sasl = "SASL" in protocol
        mechanism = self.sasl_mechanism_combo.currentText() if is_sasl else None
        is_gssapi = mechanism == "GSSAPI"
        
        return ClusterConnection(
            name=self.name_edit.text().strip(),
            bootstrap_servers=self.servers_edit.text().strip(),
            security_protocol=protocol,
            sasl_mechanism=mechanism,
            # PLAIN/SCRAM 认证
            sasl_username=self.sasl_username_edit.text().strip() if is_sasl and not is_gssapi else None,
            sasl_password=self.sasl_password_edit.text() if is_sasl and not is_gssapi else None,
            # Kerberos (GSSAPI) 认证
            sasl_kerberos_service_name=self.kerberos_service_edit.text().strip() or None if is_sasl and is_gssapi else None,
            sasl_kerberos_domain_name=self.kerberos_domain_edit.text().strip() or None if is_sasl and is_gssapi else None,
            ssl_cafile=self.ssl_ca_edit.text().strip() if "SSL" in protocol else None,
            ssl_certfile=self.ssl_cert_edit.text().strip() if "SSL" in protocol else None,
            ssl_keyfile=self.ssl_key_edit.text().strip() if "SSL" in protocol else None
        )
    
    def test_connection(self):
        """测试连接"""
        try:
            conn = self.get_connection()
            from kafka_client import KafkaClusterClient
            client = KafkaClusterClient(conn)
            client.connect()
            client.disconnect()
            
            QMessageBox.information(self, "成功", "连接测试成功！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"连接测试失败:\n{str(e)}")
    
    def save_connection(self):
        """保存连接"""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "警告", "请输入连接名称")
            return
        
        if not self.servers_edit.text().strip():
            QMessageBox.warning(self, "警告", "请输入Bootstrap Servers")
            return
        
        self.accept()


class CreateTopicDialog(QDialog):
    """创建Topic对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("创建 Topic")
        self.setMinimumWidth(400)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # 标题
        title = QLabel("创建新 Topic")
        title.setProperty("heading", True)
        layout.addWidget(title)
        
        # 表单
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("输入Topic名称")
        form_layout.addRow("Topic名称:", self.name_edit)
        
        self.partitions_spin = QSpinBox()
        self.partitions_spin.setRange(1, 1000)
        self.partitions_spin.setValue(3)
        form_layout.addRow("分区数:", self.partitions_spin)
        
        self.replication_spin = QSpinBox()
        self.replication_spin.setRange(1, 10)
        self.replication_spin.setValue(1)
        form_layout.addRow("副本因子:", self.replication_spin)
        
        layout.addLayout(form_layout)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setProperty("secondary", True)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        create_btn = QPushButton("创建")
        create_btn.clicked.connect(self.create_topic)
        btn_layout.addWidget(create_btn)
        
        layout.addLayout(btn_layout)
    
    def create_topic(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "警告", "请输入Topic名称")
            return
        self.accept()
    
    def get_topic_config(self) -> dict:
        return {
            'name': self.name_edit.text().strip(),
            'partitions': self.partitions_spin.value(),
            'replication_factor': self.replication_spin.value()
        }


class MessageProducerDialog(QDialog):
    """消息发送对话框"""
    
    def __init__(self, parent=None, topic: str = ""):
        super().__init__(parent)
        self.topic = topic
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("发送消息")
        self.setMinimumSize(600, 500)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # 标题
        title = QLabel("发送消息")
        title.setProperty("heading", True)
        layout.addWidget(title)
        
        # Topic
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        self.topic_edit = QLineEdit()
        self.topic_edit.setText(self.topic)
        form_layout.addRow("Topic:", self.topic_edit)
        
        self.partition_spin = QSpinBox()
        self.partition_spin.setRange(-1, 1000)
        self.partition_spin.setValue(-1)
        self.partition_spin.setSpecialValueText("自动")
        form_layout.addRow("分区:", self.partition_spin)
        
        layout.addLayout(form_layout)
        
        # Key
        key_group = QGroupBox("消息 Key (可选)")
        key_layout = QVBoxLayout(key_group)
        self.key_edit = QLineEdit()
        self.key_edit.setPlaceholderText("输入消息Key")
        key_layout.addWidget(self.key_edit)
        layout.addWidget(key_group)
        
        # Value
        value_group = QGroupBox("消息内容")
        value_layout = QVBoxLayout(value_group)
        self.value_edit = QTextEdit()
        self.value_edit.setPlaceholderText("输入消息内容 (支持JSON)")
        self.value_edit.setMinimumHeight(200)
        value_layout.addWidget(self.value_edit)
        layout.addWidget(value_group)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setProperty("secondary", True)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        send_btn = QPushButton("发送")
        send_btn.clicked.connect(self.send_message)
        btn_layout.addWidget(send_btn)
        
        layout.addLayout(btn_layout)
    
    def send_message(self):
        if not self.topic_edit.text().strip():
            QMessageBox.warning(self, "警告", "请输入Topic名称")
            return
        
        if not self.value_edit.toPlainText().strip():
            QMessageBox.warning(self, "警告", "请输入消息内容")
            return
        
        self.accept()
    
    def get_message_data(self) -> dict:
        partition = self.partition_spin.value()
        return {
            'topic': self.topic_edit.text().strip(),
            'key': self.key_edit.text().strip() if self.key_edit.text().strip() else None,
            'value': self.value_edit.toPlainText(),
            'partition': partition if partition >= 0 else None
        }


class MessageDetailDialog(QDialog):
    """消息详情对话框"""
    
    # 重新发送信号: topic, key, value, headers
    resend_requested = pyqtSignal(str, object, object, object)
    # 请求检查消费状态信号: topic, partition, offset
    check_consumption_requested = pyqtSignal(str, int, int)
    
    def __init__(self, parent=None, message=None):
        super().__init__(parent)
        self.message = message
        self.setup_ui()
        
        if message:
            self.load_message(message, emit_signal=False)
    
    def setup_ui(self):
        self.setWindowTitle("消息详情")
        self.setMinimumSize(800, 700)
        self.resize(900, 750)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # 标题
        title = QLabel("📨 消息详情")
        title.setProperty("heading", True)
        layout.addWidget(title)
        
        # 元数据
        meta_group = QGroupBox("元数据")
        meta_layout = QFormLayout(meta_group)
        meta_layout.setSpacing(8)
        
        self.topic_label = QLabel()
        self.topic_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        meta_layout.addRow("Topic:", self.topic_label)
        
        self.partition_label = QLabel()
        meta_layout.addRow("分区:", self.partition_label)
        
        self.offset_label = QLabel()
        meta_layout.addRow("Offset:", self.offset_label)
        
        self.timestamp_label = QLabel()
        meta_layout.addRow("时间戳:", self.timestamp_label)
        
        layout.addWidget(meta_group)
        
        # 消费信息表格
        consumption_group = QGroupBox("消费信息")
        consumption_layout = QVBoxLayout(consumption_group)
        consumption_layout.setContentsMargins(8, 16, 8, 8)
        
        self.consumption_table = QTableWidget()
        self.consumption_table.setColumnCount(3)
        self.consumption_table.setHorizontalHeaderLabels(["消费组", "消费情况", "消费时间"])
        # 消费组列：使用 Stretch 模式占据剩余空间
        self.consumption_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        # 消费情况列：设置合理宽度
        self.consumption_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.consumption_table.setColumnWidth(1, 120)
        # 消费时间列：设置合理宽度
        self.consumption_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.consumption_table.setColumnWidth(2, 180)
        # 设置表格高度，允许滚动
        self.consumption_table.setMinimumHeight(150)
        self.consumption_table.setMaximumHeight(300)
        # 确保表格使用主题背景
        self.consumption_table.setAlternatingRowColors(False)
        # 启用垂直滚动条
        self.consumption_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        # 只设置必要的样式，让表格继承全局主题样式
        self.consumption_table.setStyleSheet("""
            QTableWidget::item {
                padding: 10px 12px;
            }
            QHeaderView::section {
                padding: 10px 10px;
                min-height: 40px;
            }
        """)
        self.consumption_table.setRowCount(1)
        self.consumption_table.setItem(0, 0, QTableWidgetItem("检查中..."))
        self.consumption_table.setItem(0, 1, QTableWidgetItem(""))
        self.consumption_table.setItem(0, 2, QTableWidgetItem(""))
        # 设置行高
        self.consumption_table.setRowHeight(0, 40)
        consumption_layout.addWidget(self.consumption_table)
        
        layout.addWidget(consumption_group)
        
        # 标签页
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Key 标签页
        key_tab = QWidget()
        key_layout = QVBoxLayout(key_tab)
        key_layout.setContentsMargins(0, 16, 0, 0)
        
        self.key_text = QTextEdit()
        self.key_text.setReadOnly(True)
        self.key_text.setPlaceholderText("(空)")
        self.key_text.setMinimumHeight(300)
        key_layout.addWidget(self.key_text)
        
        tab_widget.addTab(key_tab, "Key")
        
        # Value 标签页
        value_tab = QWidget()
        value_layout = QVBoxLayout(value_tab)
        value_layout.setContentsMargins(0, 16, 0, 0)
        
        self.value_text = QTextEdit()
        self.value_text.setReadOnly(True)
        self.value_text.setPlaceholderText("(空)")
        self.value_text.setMinimumHeight(300)
        value_layout.addWidget(self.value_text)
        
        tab_widget.addTab(value_tab, "Value")
        
        # Headers 标签页
        headers_tab = QWidget()
        headers_layout = QVBoxLayout(headers_tab)
        headers_layout.setContentsMargins(0, 16, 0, 0)
        
        self.headers_text = QTextEdit()
        self.headers_text.setReadOnly(True)
        self.headers_text.setPlaceholderText("(无)")
        self.headers_text.setMinimumHeight(300)
        headers_layout.addWidget(self.headers_text)
        
        tab_widget.addTab(headers_tab, "Headers")
        
        # 默认选中 Value 标签页
        tab_widget.setCurrentIndex(1)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        copy_btn = QPushButton("复制 Value")
        copy_btn.setProperty("secondary", True)
        copy_btn.clicked.connect(self.copy_value)
        btn_layout.addWidget(copy_btn)
        
        resend_btn = QPushButton("重新发送")
        resend_btn.setProperty("secondary", True)
        resend_btn.clicked.connect(self.resend_message)
        btn_layout.addWidget(resend_btn)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
    
    def load_message(self, msg, emit_signal=True):
        """加载消息内容"""
        self.topic_label.setText(msg.topic)
        self.partition_label.setText(str(msg.partition))
        self.offset_label.setText(str(msg.offset))
        self.timestamp_label.setText(msg.timestamp_str if msg.timestamp_str else "-")
        
        self.key_text.setPlainText(msg.key_str() if msg.key_str() else "")
        self.value_text.setPlainText(msg.value_str() if msg.value_str() else "")
        
        if msg.headers:
            headers_str = "\n".join([f"{k}: {v}" for k, v in msg.headers])
            self.headers_text.setPlainText(headers_str)
        else:
            self.headers_text.setPlainText("")
        
        # 请求检查消费状态
        if emit_signal:
            self.request_consumption_check()
    
    def request_consumption_check(self):
        """请求检查消费状态"""
        if self.message:
            self.check_consumption_requested.emit(
                self.message.topic, 
                self.message.partition, 
                self.message.offset
            )
    
    def update_consumption_status(self, consumed_by):
        """更新消费状态显示"""
        self.consumption_table.setRowCount(0)
        
        if not consumed_by:
            self.consumption_table.setRowCount(1)
            self.consumption_table.setItem(0, 0, QTableWidgetItem("-"))
            status_item = QTableWidgetItem("未消费")
            status_item.setForeground(Qt.GlobalColor.red)
            self.consumption_table.setItem(0, 1, status_item)
            self.consumption_table.setItem(0, 2, QTableWidgetItem("-"))
            # 设置行高
            self.consumption_table.setRowHeight(0, 40)
        else:
            self.consumption_table.setRowCount(len(consumed_by))
            for i, group in enumerate(consumed_by):
                self.consumption_table.setItem(i, 0, QTableWidgetItem(group['group_id']))
                status_item = QTableWidgetItem("已消费")
                status_item.setForeground(Qt.GlobalColor.green)
                self.consumption_table.setItem(i, 1, status_item)
                
                # 显示消费时间
                consumption_time = group.get('consumption_time')
                if consumption_time:
                    if isinstance(consumption_time, datetime):
                        time_str = consumption_time.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        time_str = str(consumption_time)
                else:
                    time_str = "-"
                self.consumption_table.setItem(i, 2, QTableWidgetItem(time_str))
                # 设置行高
                self.consumption_table.setRowHeight(i, 40)
    
    def copy_value(self):
        """复制 Value 到剪贴板"""
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.value_text.toPlainText())
        QMessageBox.information(self, "成功", "Value 已复制到剪贴板")
    
    def resend_message(self):
        """重新发送消息"""
        if not self.message:
            QMessageBox.warning(self, "警告", "没有消息可发送")
            return
        
        self.resend_requested.emit(
            self.message.topic,
            self.message.key,
            self.message.value,
            self.message.headers
        )
        self.accept()

