"""
独立进程：启动 MQTT 监听线程 + 异步队列消费者，将遥测数据写入 IotTelemetry。

用法（在项目根目录）:
  uv run python tools/run_mqtt_consumer.py

依赖：paho-mqtt（可选，未安装时仅打印说明）。
"""
from __future__ import annotations

import asyncio
import logging
import sys

# 确保 app 可导入
sys.path.insert(0, "src/py")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def consume_mqtt_queue() -> None:
    """从全局 MQTT 队列取消息并写入数据库。"""
    from app.config import alchemy
    from app.domain.carbon.collectors.mqtt_adapter import get_mqtt_queue, save_telemetry_from_payload

    queue = get_mqtt_queue()
    loop = asyncio.get_event_loop()
    while True:
        try:
            try:
                item = await loop.run_in_executor(None, lambda: queue.get(timeout=2.0))
            except Exception:
                await asyncio.sleep(0.2)
                continue
            site_id, device_id, payload = item
            await save_telemetry_from_payload(alchemy.get_session, site_id, device_id, payload)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.exception("处理 MQTT 队列消息失败: %s", e)


def main() -> None:
    from app.domain.carbon.collectors.mqtt_adapter import MqttAdapter, PAHO_AVAILABLE

    if not PAHO_AVAILABLE:
        logger.warning("未安装 paho-mqtt，请执行: uv add paho-mqtt")
        return

    adapter = MqttAdapter()
    adapter.start_background()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(consume_mqtt_queue())
    except KeyboardInterrupt:
        logger.info("收到中断，退出")
    finally:
        adapter.stop()
        loop.close()


if __name__ == "__main__":
    main()
