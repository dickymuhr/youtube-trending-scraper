from typing import Dict, List
import json
from kafka import KafkaConsumer

from comment import Comment
from video import Video
from settings import BOOTSTRAP_SERVERS, KAFKA_TOPIC

class JsonConsumer:
    def __init__(self, props:Dict):
        self.consumer = KafkaConsumer(**props)

    def consume_from_kafka(self, topics: List[str]):
        self.consumer.subscribe(topics)
        print("Start consuming Kafka")
        print("Topics available: ", self.consumer.subscription())
        while True:
            try:
                message = self.consumer.poll(1.0)
                if message is None or message == {}:
                    continue
                for message_key, message_value in message.items():
                    for msg_val in message_value:
                        # print(msg_val.key)
                        # print(json.dumps(msg_val.value.__dict__["video_id"], default=str,  indent=2))
                        yield msg_val.value.__dict__
            except KeyboardInterrupt:
                break

        self.consumer.close()

if __name__ == '__main__':
    config = {
        'bootstrap_servers': BOOTSTRAP_SERVERS,
        'auto_offset_reset': 'earliest',
        'enable_auto_commit': True,
        'key_deserializer': lambda key: str(key.decode('utf-8')),
        'value_deserializer': lambda x: json.loads(x.decode('utf-8'), object_hook=lambda d: Video.from_dict(d)),
        'group_id': 'consumer.group.id.json-trend.1',
    }

    json_consumer = JsonConsumer(props=config)
    total_trend_comment = 0
    total_comment = 0
    for message in json_consumer.consume_from_kafka(topics=[KAFKA_TOPIC]):
        # print(json.dumps(message, default=str,  indent=2))
        total_trend_comment+=message["comment_count"]
        total_comment+=1
        print(f"{message['video_id']}:{message['comment_count']}")
        print(total_comment)

    print(total_trend_comment)