import json, os
from dotenv import load_dotenv
import trend_scraper
from typing import List, Dict
from kafka import KafkaProducer
from kafka.errors import KafkaTimeoutError
from video import Video

from settings import BOOTSTRAP_SERVERS, KAFKA_TOPIC

class JsonProducer(KafkaProducer):
    def __init__(self, props: Dict):
        self.producer = KafkaProducer(**props)

    def publish_trends(self, topic: str, messages: List[Video]):
        for video in messages:
            try:
                record = self.producer.send(topic=topic, key=video.video_id, value=video)
                print(f"Record {video.video_id} succesfully produced at offset {record.get().offset}")
            except KafkaTimeoutError as e:
                print(e.__str__())

if __name__ == "__main__":
    config = {
        'bootstrap_servers': BOOTSTRAP_SERVERS,
        'key_serializer': lambda key: str(key).encode(),
        'value_serializer': lambda x: json.dumps(x.__dict__, default=str).encode('utf-8')
    }

    # Define producer
    producer = JsonProducer(props=config)

    # Call scraper
    load_dotenv()
    api_key = os.getenv("YOUTUBE_API_KEY")
    country_code = "ID" # Indonesia

    youtube_trending_data = trend_scraper.get_data(country_code, api_key)

    # Publish
    producer.publish_trends(topic=KAFKA_TOPIC, messages=youtube_trending_data)