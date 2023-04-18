from dotenv import load_dotenv
import requests, os, sys, json, datetime
from typing import List
from settings import VIDEO_ID_EX
from comment import Comment

def api_request(page_token,video_id, api_key):
     
    request_url = f"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet,replies{page_token}videoId={video_id}&maxResults=100&key={api_key}"
    while True:
            
        try:
            request = requests.get(request_url, timeout=6)
            print(f"Response Success. Status Code: {request.status_code}")
            request.raise_for_status()
            break
        except requests.exceptions.Timeout as e:
            print("Request timeout. Retrying after 5 second..")
            pass
        except requests.exceptions.HTTPError as e:
            if request.status_code == 429:
                print("Temp-Banned due to excess requests, please wait and continue later")
                sys.exit()
            else:
                raise e

    return request.json()

def get_comments(items, is_reply = False, replied_to=None):
    # do it recursively because there are nested comments in replies
    data_comments = []
    for comment in items:
        total_reply = comment['snippet'].get('totalReplyCount',0)
        comment_level = comment['snippet']['topLevelComment'] if not(is_reply) else comment # top level or reply level
        comment_id = comment_level['id']
        snippet = comment_level['snippet']
        video_id = snippet['videoId']
        text = snippet['textOriginal']
        author = snippet['authorDisplayName']
        published = datetime.datetime.fromisoformat(snippet.get("publishedAt","")[:-1])
        total_like = snippet['likeCount']

        feature = [comment_id, video_id, text, author, published, total_like, total_reply, is_reply, replied_to]

        data_comments.append(Comment(feature))
        # look for replies
        if total_reply > 0:
            replies = comment['replies']
            replies_items = replies.get('comments',[])
            data_comments.extend(get_comments(replies_items, is_reply=True, replied_to=author))
    return data_comments

def get_pages(video_id, api_key, next_page_token="&"):
    video_comment = []

    while next_page_token is not None:
        comment_data_page = api_request(next_page_token, video_id, api_key)

        next_page_token = comment_data_page.get("nextPageToken", None)
        next_page_token = f"&pageToken={next_page_token}&" if next_page_token is not None else next_page_token

        items = comment_data_page.get('items',[])
        comments_data = get_comments(items)
        video_comment.extend(comments_data)
    return video_comment

def get_data(video_id:List, api_key):
    data_list = []
    for id in video_id:
        comment_data = get_pages(id,api_key)
        data_list.extend(comment_data)

    return data_list

if __name__ == "__main__":

    # Load api key
    load_dotenv()
    api_key = os.getenv("YOUTUBE_API_KEY")


    youtube_comment_data = get_data(VIDEO_ID_EX, api_key)
    for data in youtube_comment_data:
        print(json.dumps(data.__dict__, default=str,  indent=2))


    print(len(youtube_comment_data))