"""对话框组件"""

from datetime import datetime
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QPushButton, QLabel, QSpinBox,
    QTextEdit, QGroupBox, QMessageBox, QCheckBox,
    QDialogButtonBox, QTabWidget, QWidget, QFileDialog,
    QRadioButton, QListWidget, QAbstractItemView,
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


class AddPartitionsDialog(QDialog):
    """增加分区对话框"""

    def __init__(self, parent=None, topic_name: str = "", current_partition_count: int = 1):
        super().__init__(parent)
        self.topic_name = topic_name
        self.current_count = current_partition_count
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("增加分区")
        self.setMinimumWidth(400)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("增加 Topic 分区数")
        title.setProperty("heading", True)
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)

        self.topic_label = QLabel(self.topic_name)
        form.addRow("Topic:", self.topic_label)

        self.current_label = QLabel(str(self.current_count))
        form.addRow("当前分区数:", self.current_label)

        self.new_partitions_spin = QSpinBox()
        self.new_partitions_spin.setRange(self.current_count + 1, 1000)
        self.new_partitions_spin.setValue(min(self.current_count + 1, 1000))
        form.addRow("新分区总数:", self.new_partitions_spin)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("取消")
        cancel_btn.setProperty("secondary", True)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)

    def get_new_total_partitions(self) -> int:
        return self.new_partitions_spin.value()


class ResetOffsetDialog(QDialog):
    """重置消费点对话框"""

    def __init__(self, parent=None, group_id: str = "", has_selection: bool = False, partition_count: int = 0):
        super().__init__(parent)
        self.group_id = group_id
        self.has_selection = has_selection
        self.partition_count = partition_count
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("重置消费点")
        self.setMinimumWidth(420)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("重置消费者组消费点")
        title.setProperty("heading", True)
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)
        self.group_label = QLabel(self.group_id)
        form.addRow("消费者组:", self.group_label)
        layout.addLayout(form)

        target_group = QGroupBox("重置到")
        target_layout = QVBoxLayout(target_group)
        self.target_earliest = QRadioButton("最早 (earliest) — 从分区起始位置开始消费")
        self.target_latest = QRadioButton("最新 (latest) — 从分区末尾开始消费，跳过已有消息")
        self.target_earliest.setChecked(True)
        target_layout.addWidget(self.target_earliest)
        target_layout.addWidget(self.target_latest)
        layout.addWidget(target_group)

        scope_group = QGroupBox("范围")
        scope_layout = QVBoxLayout(scope_group)
        self.scope_all = QRadioButton(f"全部分区 ({self.partition_count} 个)")
        self.scope_selected = QRadioButton("仅当前选中的行")
        self.scope_all.setChecked(True)
        self.scope_selected.setEnabled(self.has_selection)
        if not self.has_selection:
            self.scope_selected.setToolTip("请在下方 Offset 表格中选中要重置的分区")
        scope_layout.addWidget(self.scope_all)
        scope_layout.addWidget(self.scope_selected)
        layout.addWidget(scope_group)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("取消")
        cancel_btn.setProperty("secondary", True)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)

    def get_target(self) -> str:
        return "earliest" if self.target_earliest.isChecked() else "latest"

    def get_scope(self) -> str:
        return "selected" if self.scope_selected.isChecked() else "all"


class CreateConsumerGroupDialog(QDialog):
    """创建消费者组对话框"""

    def __init__(self, parent=None, topic_names: list = None):
        super().__init__(parent)
        self.topic_names = topic_names or []
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("创建消费者组")
        self.setMinimumSize(440, 420)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("创建新消费者组")
        title.setProperty("heading", True)
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)
        self.group_id_edit = QLineEdit()
        self.group_id_edit.setPlaceholderText("输入消费者组 ID，如 my-consumer-group")
        form.addRow("消费者组 ID:", self.group_id_edit)
        layout.addLayout(form)

        topics_label = QLabel("订阅的 Topic（可多选）:")
        layout.addWidget(topics_label)
        self.topics_list = QListWidget()
        self.topics_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.topics_list.setMinimumHeight(160)
        for name in sorted(self.topic_names):
            self.topics_list.addItem(name)
        layout.addWidget(self.topics_list)

        target_group = QGroupBox("初始消费点")
        target_layout = QVBoxLayout(target_group)
        self.target_earliest = QRadioButton("最早 (earliest) — 从分区起始位置开始消费")
        self.target_latest = QRadioButton("最新 (latest) — 从分区末尾开始，跳过已有消息")
        self.target_latest.setChecked(True)
        target_layout.addWidget(self.target_earliest)
        target_layout.addWidget(self.target_latest)
        layout.addWidget(target_group)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("取消")
        cancel_btn.setProperty("secondary", True)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        create_btn = QPushButton("创建")
        create_btn.clicked.connect(self._on_create)
        btn_layout.addWidget(create_btn)
        layout.addLayout(btn_layout)

    def _on_create(self):
        if not self.group_id_edit.text().strip():
            QMessageBox.warning(self, "警告", "请输入消费者组 ID")
            return
        selected = self.get_selected_topics()
        if not selected:
            QMessageBox.warning(self, "警告", "请至少选择一个 Topic")
            return
        self.accept()

    def get_group_id(self) -> str:
        return self.group_id_edit.text().strip()

    def get_selected_topics(self) -> list:
        return [item.text() for item in self.topics_list.selectedItems()]

    def get_target(self) -> str:
        return "earliest" if self.target_earliest.isChecked() else "latest"


class ConsumeMessagesDialog(QDialog):
    """消费消息对话框（选择 Topic、分区、消费者组后打开消息浏览器并拉取）"""

    def __init__(self, parent=None, topic_names: list = None, group_names: list = None):
        super().__init__(parent)
        self.topic_names = topic_names or []
        self.group_names = group_names or []
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("消费消息")
        self.setMinimumWidth(420)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("消费消息")
        title.setProperty("heading", True)
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)

        self.topic_combo = QComboBox()
        self.topic_combo.setEditable(True)
        self.topic_combo.setPlaceholderText("选择或输入 Topic 名称")
        for name in sorted(self.topic_names):
            self.topic_combo.addItem(name)
        form.addRow("Topic:", self.topic_combo)

        self.partition_spin = QSpinBox()
        self.partition_spin.setRange(-1, 1000)
        self.partition_spin.setValue(-1)
        self.partition_spin.setSpecialValueText("全部")
        form.addRow("分区:", self.partition_spin)

        self.group_combo = QComboBox()
        self.group_combo.addItem("无(匿名)")
        for gid in sorted(self.group_names):
            self.group_combo.addItem(gid)
        form.addRow("消费者组:", self.group_combo)
        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("取消")
        cancel_btn.setProperty("secondary", True)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self._on_ok)
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)

    def _on_ok(self):
        topic = self.get_topic()
        if not topic:
            QMessageBox.warning(self, "警告", "请选择或输入 Topic 名称")
            return
        self.accept()

    def get_topic(self) -> str:
        return self.topic_combo.currentText().strip()

    def get_partition(self) -> int:
        return self.partition_spin.value()

    def get_group_id(self) -> Optional[str]:
        text = self.group_combo.currentText().strip()
        if not text or text == "无(匿名)":
            return None
        return text


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
        
        # 消费状态（合并到元数据）
        self.consumption_status_label = QLabel("检查中...")
        self.consumption_status_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.consumption_status_label.setWordWrap(True)
        meta_layout.addRow("消费状态:", self.consumption_status_label)
        
        layout.addWidget(meta_group)
        
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
        """更新消费状态显示（已合并到元数据）"""
        if not consumed_by:
            self.consumption_status_label.setText("未消费")
            self.consumption_status_label.setStyleSheet("color: #f44336;")  # 红色
        else:
            # 已消费：显示消费者和消费时间
            lines = []
            for group in consumed_by:
                consumption_time = group.get('consumption_time')
                if consumption_time:
                    if isinstance(consumption_time, datetime):
                        time_str = consumption_time.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        time_str = str(consumption_time)
                else:
                    time_str = "-"
                lines.append(f"{group['group_id']} · {time_str}")
            self.consumption_status_label.setText("\n".join(lines))
            self.consumption_status_label.setStyleSheet("color: #4caf50;")  # 绿色
    
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

