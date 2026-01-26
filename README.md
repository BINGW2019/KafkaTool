# Kafka Offset Explorer

一个使用 Python + PyQt6 实现的 Kafka 集群管理和监控工具。

## 功能特性

- 🔗 **连接管理**: 支持多个 Kafka 集群连接配置
- 📋 **Topic 浏览**: 查看 Topics 列表、分区信息、配置详情
- 👥 **Consumer Groups**: 监控消费者组、查看 offset 和 lag
- 📨 **消息浏览**: 实时查看 Topic 中的消息内容
- ✉️ **消息发送**: 向指定 Topic 发送消息

## 安装

```bash
pip install -r requirements.txt
```

## 运行

```bash
python main.py
```

## 截图

启动后，您将看到一个现代化的深色主题界面，左侧为集群导航树，右侧为详情面板。

## 系统要求

- Python 3.9+
- PyQt6
- kafka-python 或 confluent-kafka

