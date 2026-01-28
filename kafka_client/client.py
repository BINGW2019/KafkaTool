"""Kafka客户端封装"""

import logging
from typing import List, Optional, Dict, Any, Callable, Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import threading

from kafka import KafkaConsumer, KafkaProducer, KafkaAdminClient
from kafka.admin import NewTopic, ConfigResource, ConfigResourceType
from kafka.admin.new_partitions import NewPartitions
from kafka.errors import KafkaError
from kafka.structs import TopicPartition

from .models import (
    ClusterConnection,
    TopicInfo,
    PartitionInfo,
    ConsumerGroupInfo,
    ConsumerGroupMember,
    ConsumerGroupOffset,
    KafkaMessage,
    BrokerInfo
)

logger = logging.getLogger(__name__)


class KafkaClusterClient:
    """Kafka集群客户端封装"""
    
    def __init__(self, connection: ClusterConnection):
        self.connection = connection
        self._admin_client: Optional[KafkaAdminClient] = None
        self._consumer: Optional[KafkaConsumer] = None
        self._producer: Optional[KafkaProducer] = None
        self._connected = False
        self._lock = threading.Lock()
        
    @property
    def is_connected(self) -> bool:
        return self._connected
    
    def connect(self) -> bool:
        """建立连接"""
        try:
            config = self.connection.get_kafka_config()
            self._admin_client = KafkaAdminClient(**config)
            self._connected = True
            logger.info(f"成功连接到Kafka集群: {self.connection.name}")
            return True
        except Exception as e:
            logger.error(f"连接Kafka失败: {e}")
            self._connected = False
            raise
    
    def disconnect(self):
        """断开连接"""
        try:
            if self._admin_client:
                self._admin_client.close()
            if self._consumer:
                self._consumer.close()
            if self._producer:
                self._producer.close()
        except Exception as e:
            logger.error(f"断开连接时出错: {e}")
        finally:
            self._admin_client = None
            self._consumer = None
            self._producer = None
            self._connected = False
    
    def _get_consumer(self, group_id: str = None) -> KafkaConsumer:
        """获取Consumer实例"""
        config = self.connection.get_kafka_config()
        config['enable_auto_commit'] = False
        config['auto_offset_reset'] = 'earliest'
        if group_id:
            config['group_id'] = group_id
        return KafkaConsumer(**config)
    
    def _get_producer(self) -> KafkaProducer:
        """获取Producer实例"""
        if not self._producer:
            config = self.connection.get_kafka_config()
            self._producer = KafkaProducer(**config)
        return self._producer
    
    def get_brokers(self) -> List[BrokerInfo]:
        """获取Broker列表"""
        if not self._admin_client:
            raise RuntimeError("未连接到Kafka集群")
        
        brokers = []
        cluster_metadata = self._admin_client.describe_cluster()
        
        for broker in cluster_metadata.get('brokers', []):
            brokers.append(BrokerInfo(
                node_id=broker['node_id'],
                host=broker['host'],
                port=broker['port'],
                rack=broker.get('rack')
            ))
        
        return sorted(brokers, key=lambda x: x.node_id)
    
    def get_topic_names(self, include_internal: bool = False) -> List[str]:
        """获取Topic名称列表（轻量级，只获取名称）"""
        if not self._admin_client:
            raise RuntimeError("未连接到Kafka集群")
        
        topic_metadata = self._admin_client.list_topics()
        topics = []
        
        for topic_name in topic_metadata:
            if topic_name.startswith('__') and not include_internal:
                continue
            topics.append(topic_name)
        
        return sorted(topics)
    
    def get_consumer_group_names(self) -> List[tuple]:
        """获取消费者组名称列表（轻量级，只获取名称和状态）"""
        if not self._admin_client:
            raise RuntimeError("未连接到Kafka集群")
        
        groups = []
        group_list = self._admin_client.list_consumer_groups()
        
        for group_id, protocol_type in group_list:
            groups.append((group_id, protocol_type or ""))
        
        return sorted(groups, key=lambda x: x[0])
    
    def get_topics(self, include_internal: bool = False) -> List[TopicInfo]:
        """获取Topic列表（包含详细信息）"""
        if not self._admin_client:
            raise RuntimeError("未连接到Kafka集群")
        
        topics = []
        topic_metadata = self._admin_client.list_topics()
        
        # 获取Topic详情
        consumer = self._get_consumer()
        try:
            for topic_name in topic_metadata:
                if topic_name.startswith('__') and not include_internal:
                    continue
                
                partitions_metadata = consumer.partitions_for_topic(topic_name)
                if partitions_metadata is None:
                    continue
                
                partition_list = []
                for partition_id in partitions_metadata:
                    tp = TopicPartition(topic_name, partition_id)
                    
                    # 获取offset信息
                    beginning = consumer.beginning_offsets([tp])
                    end = consumer.end_offsets([tp])
                    
                    partition_list.append(PartitionInfo(
                        partition_id=partition_id,
                        leader=-1,  # 需要额外API获取
                        replicas=[],
                        isr=[],
                        beginning_offset=beginning.get(tp, 0),
                        end_offset=end.get(tp, 0)
                    ))
                
                topics.append(TopicInfo(
                    name=topic_name,
                    partitions=sorted(partition_list, key=lambda x: x.partition_id),
                    is_internal=topic_name.startswith('__')
                ))
        finally:
            consumer.close()
        
        return sorted(topics, key=lambda x: x.name)
    
    def get_topic_detail(self, topic_name: str) -> Optional[TopicInfo]:
        """获取Topic详细信息"""
        if not self._admin_client:
            raise RuntimeError("未连接到Kafka集群")
        
        consumer = self._get_consumer()
        try:
            partitions_metadata = consumer.partitions_for_topic(topic_name)
            if partitions_metadata is None:
                return None
            
            partition_list = []
            for partition_id in partitions_metadata:
                tp = TopicPartition(topic_name, partition_id)
                beginning = consumer.beginning_offsets([tp])
                end = consumer.end_offsets([tp])
                
                partition_list.append(PartitionInfo(
                    partition_id=partition_id,
                    leader=-1,
                    replicas=[],
                    isr=[],
                    beginning_offset=beginning.get(tp, 0),
                    end_offset=end.get(tp, 0)
                ))
            
            # 获取Topic配置
            config = {}
            try:
                resource = ConfigResource(ConfigResourceType.TOPIC, topic_name)
                configs = self._admin_client.describe_configs([resource])
                for res, future in configs.items():
                    config_entries = future.result()
                    for entry in config_entries:
                        config[entry.name] = entry.value
            except Exception as e:
                logger.warning(f"获取Topic配置失败: {e}")
            
            return TopicInfo(
                name=topic_name,
                partitions=sorted(partition_list, key=lambda x: x.partition_id),
                config=config,
                is_internal=topic_name.startswith('__')
            )
        finally:
            consumer.close()
    
    def get_consumer_groups(self) -> List[ConsumerGroupInfo]:
        """获取消费者组列表"""
        if not self._admin_client:
            raise RuntimeError("未连接到Kafka集群")
        
        groups = []
        group_ids = self._admin_client.list_consumer_groups()
        
        for group_id, protocol_type in group_ids:
            try:
                group_info = self.get_consumer_group_detail(group_id)
                if group_info:
                    groups.append(group_info)
            except Exception as e:
                logger.warning(f"获取消费者组 {group_id} 信息失败: {e}")
                groups.append(ConsumerGroupInfo(
                    group_id=group_id,
                    state="Unknown",
                    protocol_type=protocol_type or "",
                    protocol=""
                ))
        
        return sorted(groups, key=lambda x: x.group_id)
    
    def get_consumer_group_detail(self, group_id: str) -> Optional[ConsumerGroupInfo]:
        """获取消费者组详细信息"""
        if not self._admin_client:
            raise RuntimeError("未连接到Kafka集群")
        
        try:
            # 获取组描述
            descriptions = self._admin_client.describe_consumer_groups([group_id])
            if not descriptions:
                return None
            
            desc = descriptions[0]
            
            # 调试：打印可用属性
            logger.debug(f"GroupInformation attributes: {dir(desc)}")
            
            members = []
            # 成员列表可能在不同属性中
            member_list = getattr(desc, 'members', [])
            for member in member_list:
                assigned = []
                member_assignment = getattr(member, 'member_assignment', None)
                if member_assignment:
                    try:
                        if hasattr(member_assignment, 'assignment'):
                            for topic, partitions in member_assignment.assignment:
                                for p in partitions:
                                    assigned.append({'topic': topic, 'partition': p})
                    except:
                        pass
                
                members.append(ConsumerGroupMember(
                    member_id=getattr(member, 'member_id', ''),
                    client_id=getattr(member, 'client_id', ''),
                    client_host=getattr(member, 'client_host', ''),
                    assigned_partitions=assigned
                ))
            
            # 获取offset信息
            offsets = []
            try:
                offset_data = self._admin_client.list_consumer_group_offsets(group_id)
                consumer = self._get_consumer()
                try:
                    for tp, offset_meta in offset_data.items():
                        # 获取开始和结束 offset
                        beginning_offsets = consumer.beginning_offsets([tp])
                        end_offsets = consumer.end_offsets([tp])
                        
                        start_offset = beginning_offsets.get(tp, 0)
                        end_offset = end_offsets.get(tp, 0)
                        current_offset = offset_meta.offset if offset_meta.offset >= 0 else 0
                        
                        offsets.append(ConsumerGroupOffset(
                            topic=tp.topic,
                            partition=tp.partition,
                            current_offset=current_offset,
                            end_offset=end_offset,
                            lag=max(0, end_offset - current_offset),
                            start_offset=start_offset,
                            metadata=offset_meta.metadata or ""
                        ))
                finally:
                    consumer.close()
            except Exception as e:
                logger.warning(f"获取消费者组offset失败: {e}")
            
            # 安全获取属性，不同版本的 kafka-python 属性名可能不同
            coordinator = getattr(desc, 'coordinator', None)
            coordinator_id = None
            if coordinator:
                coordinator_id = getattr(coordinator, 'node_id', None)
            
            return ConsumerGroupInfo(
                group_id=getattr(desc, 'group', group_id),  # 回退到传入的参数
                state=getattr(desc, 'state', 'Unknown'),
                protocol_type=getattr(desc, 'protocol_type', ''),
                protocol=getattr(desc, 'protocol', ''),
                coordinator=coordinator_id,
                members=members,
                offsets=sorted(offsets, key=lambda x: (x.topic, x.partition))
            )
        except Exception as e:
            logger.error(f"获取消费者组详情失败: {e}", exc_info=True)
            return None
    
    def consume_messages(
        self,
        topic: str,
        partition: int = None,
        offset: int = None,
        limit: int = 100,
        timeout_ms: int = 5000,
        from_beginning: bool = False,
        sort_field: str = "offset",
        group_id: Optional[str] = None,
    ) -> List[KafkaMessage]:
        """消费消息。group_id 不为空时使用该消费者组的提交位点作为起始位置（不 seek）。"""
        messages = []
        consumer = self._get_consumer(group_id=group_id)
        
        try:
            if partition is not None:
                tp = TopicPartition(topic, partition)
                consumer.assign([tp])
                if group_id is None:
                    if offset is not None:
                        consumer.seek(tp, offset)
                    elif from_beginning:
                        beginning_offsets = consumer.beginning_offsets([tp])
                        consumer.seek(tp, beginning_offsets.get(tp, 0))
                    else:
                        end_offsets = consumer.end_offsets([tp])
                        end_offset = end_offsets.get(tp, 0)
                        consumer.seek(tp, max(0, end_offset - limit))
            else:
                consumer.subscribe([topic])
                consumer.poll(timeout_ms=1000)
                assigned = consumer.assignment()
                if group_id is None and assigned:
                    for tp in assigned:
                        if from_beginning:
                            beginning_offsets = consumer.beginning_offsets([tp])
                            consumer.seek(tp, beginning_offsets.get(tp, 0))
                        else:
                            end_offsets = consumer.end_offsets([tp])
                            end_offset = end_offsets.get(tp, 0)
                            consumer.seek(tp, max(0, end_offset - (limit // len(assigned))))
            
            raw_messages = consumer.poll(timeout_ms=timeout_ms, max_records=limit)
            
            for tp, msg_list in raw_messages.items():
                for msg in msg_list:
                    timestamp = None
                    if msg.timestamp and msg.timestamp > 0:
                        timestamp = datetime.fromtimestamp(msg.timestamp / 1000)
                    
                    messages.append(KafkaMessage(
                        topic=msg.topic,
                        partition=msg.partition,
                        offset=msg.offset,
                        timestamp=timestamp,
                        key=msg.key,
                        value=msg.value,
                        headers=list(msg.headers) if msg.headers else []
                    ))
            
            # 排序：from_beginning时正序，否则倒序
            if sort_field == "timestamp":
                # 按时间戳排序
                def sort_key(m):
                    if m.timestamp:
                        return m.timestamp
                    from datetime import datetime
                    return datetime.min if from_beginning else datetime.max
                messages.sort(key=sort_key, reverse=not from_beginning)
            else:
                # 按 offset 排序
                messages.sort(key=lambda x: x.offset, reverse=not from_beginning)
            
        finally:
            consumer.close()
        
        return messages[:limit]
    
    def produce_message(
        self,
        topic: str,
        value: bytes,
        key: bytes = None,
        partition: int = None,
        headers: List[tuple] = None
    ) -> bool:
        """发送消息"""
        try:
            producer = self._get_producer()
            
            future = producer.send(
                topic=topic,
                value=value,
                key=key,
                partition=partition,
                headers=headers
            )
            
            # 等待发送完成
            record_metadata = future.get(timeout=10)
            logger.info(f"消息发送成功: {topic}-{record_metadata.partition}@{record_metadata.offset}")
            return True
        except Exception as e:
            logger.error(f"消息发送失败: {e}")
            raise
    
    def get_message_consumption_status(
        self,
        topic: str,
        partition: int,
        offset: int
    ) -> List[Dict[str, Any]]:
        """获取消息的消费状态
        
        返回已消费该消息的消费者组列表，包含消费时间
        """
        consumed_by = []
        check_time = datetime.now()  # 记录检查时间作为消费时间
        
        try:
            # 获取所有消费者组
            group_ids = self._admin_client.list_consumer_groups()
            
            for group_id, _ in group_ids:
                try:
                    # 获取该组的 offset 信息
                    offset_data = self._admin_client.list_consumer_group_offsets(group_id)
                    
                    # 检查是否订阅了该 topic/partition
                    from kafka.structs import TopicPartition
                    tp = TopicPartition(topic, partition)
                    
                    if tp in offset_data:
                        committed_offset = offset_data[tp].offset
                        if committed_offset > offset:
                            consumed_by.append({
                                'group_id': group_id,
                                'committed_offset': committed_offset,
                                'consumption_time': check_time  # 添加消费时间
                            })
                except Exception as e:
                    logger.debug(f"检查消费者组 {group_id} offset 失败: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"获取消息消费状态失败: {e}")
        
        return consumed_by
    
    def create_topic(
        self,
        topic_name: str,
        num_partitions: int = 1,
        replication_factor: int = 1,
        config: Dict[str, str] = None
    ) -> bool:
        """创建Topic"""
        if not self._admin_client:
            raise RuntimeError("未连接到Kafka集群")
        
        try:
            new_topic = NewTopic(
                name=topic_name,
                num_partitions=num_partitions,
                replication_factor=replication_factor,
                topic_configs=config
            )
            self._admin_client.create_topics([new_topic])
            logger.info(f"Topic创建成功: {topic_name}")
            return True
        except Exception as e:
            logger.error(f"Topic创建失败: {e}")
            raise
    
    def delete_topic(self, topic_name: str) -> bool:
        """删除Topic"""
        if not self._admin_client:
            raise RuntimeError("未连接到Kafka集群")
        
        try:
            self._admin_client.delete_topics([topic_name])
            logger.info(f"Topic删除成功: {topic_name}")
            return True
        except Exception as e:
            logger.error(f"Topic删除失败: {e}")
            raise

    def create_partitions(self, topic_name: str, new_total_count: int) -> bool:
        """增加 Topic 分区数（指定新的分区总数，由 Broker 自动分配副本）"""
        if not self._admin_client:
            raise RuntimeError("未连接到Kafka集群")
        try:
            self._admin_client.create_partitions(
                {topic_name: NewPartitions(total_count=new_total_count, new_assignments=None)}
            )
            logger.info(f"Topic '{topic_name}' 分区数已调整为 {new_total_count}")
            return True
        except Exception as e:
            logger.error(f"增加分区失败: {e}")
            raise

    def reset_consumer_group_offsets(
        self,
        group_id: str,
        topic_partitions: List[Tuple[str, int]],
        target: str,
    ) -> bool:
        """重置消费者组在指定分区上的消费点。target: 'earliest' 或 'latest'。"""
        if not topic_partitions:
            raise ValueError("topic_partitions 不能为空")
        if target not in ("earliest", "latest"):
            raise ValueError("target 必须为 'earliest' 或 'latest'")
        tps = [TopicPartition(topic, partition) for topic, partition in topic_partitions]
        consumer = self._get_consumer(group_id=group_id)
        try:
            consumer.assign(tps)
            if target == "earliest":
                offsets = consumer.beginning_offsets(tps)
            else:
                offsets = consumer.end_offsets(tps)
            for tp in tps:
                consumer.seek(tp, offsets.get(tp, 0))
            consumer.commit()
            logger.info(f"消费者组 '{group_id}' 已重置 {len(tps)} 个分区到 {target}")
            return True
        finally:
            consumer.close()

    def create_consumer_group(
        self,
        group_id: str,
        topic_names: List[str],
        target: str = "latest",
    ) -> bool:
        """创建消费者组：用指定 group_id 订阅 topic，将消费点设为 earliest 或 latest 并提交，使组出现在集群中。"""
        if not group_id or not topic_names:
            raise ValueError("group_id 与 topic_names 不能为空")
        if target not in ("earliest", "latest"):
            raise ValueError("target 必须为 'earliest' 或 'latest'")
        consumer = self._get_consumer(group_id=group_id)
        try:
            consumer.subscribe(topic_names)
            consumer.poll(timeout_ms=5000)
            assigned = consumer.assignment()
            if not assigned:
                raise RuntimeError("未分配到任何分区，请检查 Topic 是否存在")
            if target == "earliest":
                offsets = consumer.beginning_offsets(assigned)
            else:
                offsets = consumer.end_offsets(assigned)
            for tp in assigned:
                consumer.seek(tp, offsets.get(tp, 0))
            consumer.commit()
            logger.info(f"消费者组 '{group_id}' 已创建，订阅 {len(topic_names)} 个 Topic，初始消费点: {target}")
            return True
        finally:
            consumer.close()

