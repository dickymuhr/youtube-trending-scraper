from typing import List, Dict

class Comment:
    def __init__(self,arr:List[str]):
        self.comment_id = arr[0]
        self.video_id = arr[1]
        self.text = arr[2]
        self.author = arr[3]
        self.published = arr[4]
        self.total_like = arr[5]
        self.total_reply = arr[6]
        self.is_reply = arr[7]
        self.replied_to = arr[8]

    @classmethod
    def from_dict(cls, d: Dict):
        return cls(arr=[
            d["comment_id"],
            d["video_id"],
            d["text"],
            d["author"],
            d["published"],
            d["total_like"],
            d["total_reply"],
            d["is_reply"],
            d["replied_to"]
        ])
    
def __repr__(self):
    return f"{self.__class__.__name__}:{self.__dict__}"