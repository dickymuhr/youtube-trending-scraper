from typing import List, Dict

class Video:
    def __init__(self,arr: List[str]):
        self.video_id = arr[0]
        self.title = arr[1]
        self.publishedAt = arr[2]
        self.channelId = arr[3]
        self.channelTitle = arr[4]
        self.category = arr[5]
        self.duration = arr[6]
        self.trending_date = arr[7]
        self.trending_country = arr[8]
        self.tags = arr[9]
        self.view_count = arr[10]
        self.likes = arr[11]
        self.comment_count = arr[12]
        self.thumbnail_link = arr[13]
        self.comments_disabled = arr[14]
        self.ratings_disabled = arr[15]
        self.description = arr[16]

    @classmethod
    def from_dict(cls, d: Dict):
        return cls(arr=[
            d["video_id"],
            d["title"],
            d["publishedAt"],
            d["channelId"],
            d["channelTitle"],
            d["category"],
            d["duration"],
            d["trending_date"],
            d["trending_country"],
            d["tags"],
            d["view_count"],
            d["likes"],
            d["comment_count"],
            d["thumbnail_link"],
            d["comments_disabled"],
            d["ratings_disabled"],
            d["description"]
        ])

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.__dict__}"
