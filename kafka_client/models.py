"""数据模型定义"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
import json


@dataclass
class ClusterConnection:
    """Kafka集群连接配置"""
    name: str
    bootstrap_servers: str
    security_protocol: str = "PLAINTEXT"
    sasl_mechanism: Optional[str] = None
    sasl_username: Optional[str] = None
    sasl_password: Optional[str] = None
    ssl_cafile: Optional[str] = None
    ssl_certfile: Optional[str] = None
    ssl_keyfile: Optional[str] = None
    # Kerberos (GSSAPI) 配置
    sasl_kerberos_service_name: Optional[str] = None
    sasl_kerberos_domain_name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'bootstrap_servers': self.bootstrap_servers,
            'security_protocol': self.security_protocol,
            'sasl_mechanism': self.sasl_mechanism,
            'sasl_username': self.sasl_username,
            'sasl_password': self.sasl_password,
            'ssl_cafile': self.ssl_cafile,
            'ssl_certfile': self.ssl_certfile,
            'ssl_keyfile': self.ssl_keyfile,
            'sasl_kerberos_service_name': self.sasl_kerberos_service_name,
            'sasl_kerberos_domain_name': self.sasl_kerberos_domain_name
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClusterConnection':
        # 兼容旧配置文件，过滤掉不存在的字段
        valid_fields = {
            'name', 'bootstrap_servers', 'security_protocol', 
            'sasl_mechanism', 'sasl_username', 'sasl_password',
            'ssl_cafile', 'ssl_certfile', 'ssl_keyfile',
            'sasl_kerberos_service_name', 'sasl_kerberos_domain_name'
        }
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)
    
    def get_kafka_config(self) -> Dict[str, Any]:
        """获取kafka-python客户端配置"""
        config = {
            'bootstrap_servers': self.bootstrap_servers.split(','),
            'security_protocol': self.security_protocol,
        }
        
        if self.sasl_mechanism:
            config['sasl_mechanism'] = self.sasl_mechanism
            
            # GSSAPI (Kerberos) 认证配置
            if self.sasl_mechanism == 'GSSAPI':
                if self.sasl_kerberos_service_name:
                    config['sasl_kerberos_service_name'] = self.sasl_kerberos_service_name
                if self.sasl_kerberos_domain_name:
                    config['sasl_kerberos_domain_name'] = self.sasl_kerberos_domain_name
            else:
                # PLAIN / SCRAM 认证配置
                if self.sasl_username:
                    config['sasl_plain_username'] = self.sasl_username
                if self.sasl_password:
                    config['sasl_plain_password'] = self.sasl_password
        
        if self.ssl_cafile:
            config['ssl_cafile'] = self.ssl_cafile
        if self.ssl_certfile:
            config['ssl_certfile'] = self.ssl_certfile
        if self.ssl_keyfile:
            config['ssl_keyfile'] = self.ssl_keyfile
            
        return config


@dataclass
class PartitionInfo:
    """分区信息"""
    partition_id: int
    leader: int
    replicas: List[int]
    isr: List[int]  # In-Sync Replicas
    beginning_offset: int = 0
    end_offset: int = 0
    
    @property
    def message_count(self) -> int:
        return self.end_offset - self.beginning_offset


@dataclass
class TopicInfo:
    """Topic信息"""
    name: str
    partitions: List[PartitionInfo] = field(default_factory=list)
    config: Dict[str, str] = field(default_factory=dict)
    is_internal: bool = False
    
    @property
    def partition_count(self) -> int:
        return len(self.partitions)
    
    @property
    def replication_factor(self) -> int:
        if self.partitions:
            return len(self.partitions[0].replicas)
        return 0
    
    @property
    def total_messages(self) -> int:
        return sum(p.message_count for p in self.partitions)


@dataclass
class ConsumerGroupMember:
    """消费者组成员"""
    member_id: str
    client_id: str
    client_host: str
    assigned_partitions: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ConsumerGroupOffset:
    """消费者组在某个分区的offset信息"""
    topic: str
    partition: int
    current_offset: int
    end_offset: int
    lag: int
    start_offset: int = 0
    metadata: str = ""


@dataclass
class ConsumerGroupInfo:
    """消费者组信息"""
    group_id: str
    state: str
    protocol_type: str
    protocol: str
    coordinator: Optional[int] = None
    members: List[ConsumerGroupMember] = field(default_factory=list)
    offsets: List[ConsumerGroupOffset] = field(default_factory=list)
    
    @property
    def total_lag(self) -> int:
        return sum(o.lag for o in self.offsets)
    
    @property
    def member_count(self) -> int:
        return len(self.members)


@dataclass
class KafkaMessage:
    """Kafka消息"""
    topic: str
    partition: int
    offset: int
    timestamp: Optional[datetime]
    key: Optional[bytes]
    value: Optional[bytes]
    headers: List[tuple] = field(default_factory=list)
    
    def key_str(self, encoding: str = 'utf-8') -> str:
        if self.key is None:
            return ""
        try:
            return self.key.decode(encoding)
        except:
            return self.key.hex()
    
    def value_str(self, encoding: str = 'utf-8') -> str:
        if self.value is None:
            return ""
        try:
            decoded = self.value.decode(encoding)
            # 尝试格式化JSON
            try:
                parsed = json.loads(decoded)
                return json.dumps(parsed, indent=2, ensure_ascii=False)
            except:
                return decoded
        except:
            return self.value.hex()
    
    @property
    def timestamp_str(self) -> str:
        if self.timestamp:
            return self.timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        return ""


@dataclass
class BrokerInfo:
    """Broker信息"""
    node_id: int
    host: str
    port: int
    rack: Optional[str] = None
    
    @property
    def address(self) -> str:
        return f"{self.host}:{self.port}"

