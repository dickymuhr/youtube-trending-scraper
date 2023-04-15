import requests, sys, time, os, datetime, json, re
from typing import List
from dotenv import load_dotenv
import pandas as pd
from category import CATEGORY_DICT
from settings import COUNTRY_CODES
from video import Video
import pycountry

# List of simple to collect features
snippet_features = ["title",
                    "publishedAt",
                    "channelId",
                    "channelTitle"]

# Any characters to exclude, generally these are things that become problematic in CSV files
unsafe_characters = ['\n', '"']

# Used to identify columns, currently hardcoded order
header = ["video_id"] + snippet_features + ["category","duration","trending_date", "trending_country" ,"tags", "view_count", "likes",
                                            "comment_count", "thumbnail_link", "comments_disabled",
                                            "ratings_disabled", "description"]

def prepare_feature(feature):
    # Removes any character from the unsafe characters list and surrounds the whole item in quotes
    for ch in unsafe_characters:
        feature = str(feature).replace(ch, "")
    return feature


def api_request(page_token, country_code, api_key):
    # Builds the URL and requests the JSON from it

    request_url = f"https://www.googleapis.com/youtube/v3/videos?part=id,statistics,snippet,contentDetails{page_token}chart=mostPopular&regionCode={country_code}&maxResults=50&key={api_key}"
    
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


def get_tags(tags_list):
    # Takes a list of tags, prepares each tag and joins them into a string by the pipe character
    return prepare_feature("|".join(tags_list))

def get_duration(duration_iso):
    match = re.match(r'^PT((\d+)H)?((\d+)M)?((\d+)S)?$', duration_iso)
    hours = int(match.group(2)) if match.group(2) else 0
    minutes = int(match.group(4)) if match.group(4) else 0
    seconds = int(match.group(6)) if match.group(6) else 0
    duration_seconds = (hours * 3600) + (minutes * 60) + seconds
    duration_minutes = duration_seconds / 60
    return duration_minutes


def get_videos(items,country_code):
    data_dicts = []
    for video in items:
        comments_disabled = False
        ratings_disabled = False

        # We can assume something is wrong with the video if it has no statistics, often this means it has been deleted
        # so we can just skip it
        if "statistics" not in video:
            continue

        video_id = prepare_feature(video['id'])

        # Snippet and statistics are sub-dicts of video, containing the most useful info
        snippet = video['snippet']
        statistics = video['statistics']

        # This list contains all of the features in snippet that are 1 deep and require no special processing
        features = [prepare_feature(snippet.get(feature, "")) for feature in snippet_features]

        # The following are special case features which require unique processing, or are not within the snippet dict
        category = CATEGORY_DICT[snippet.get("categoryId","0")]
        description = snippet.get("description", "")
        thumbnail_link = snippet.get("thumbnails", dict()).get("default", dict()).get("url", "")
        trending_date = time.strftime("%y.%d.%m")
        trending_country = pycountry.countries.get(alpha_2=country_code).name
        tags = get_tags(snippet.get("tags", ["[none]"]))
        view_count = statistics.get("viewCount", 0)

        content_details = video['contentDetails']
        duration  = get_duration(content_details.get("duration",0))

        # This may be unclear, essentially the way the API works is that if a video has comments or ratings disabled
        # then it has no feature for it, thus if they don't exist in the statistics dict we know they are disabled
        if 'likeCount' in statistics:
            likes = statistics['likeCount']
        else:
            ratings_disabled = True
            likes = 0

        if 'commentCount' in statistics:
            comment_count = statistics['commentCount']
        else:
            comments_disabled = True
            comment_count = 0

        # Compiles all of the various bits of info into one consistently formatted line
        line = [video_id] + features + [prepare_feature(x) for x in [category, duration,trending_date, trending_country, tags, view_count, likes,
                                                                       comment_count, thumbnail_link, comments_disabled,
                                                                       ratings_disabled, description]]
        data_dict = dict(zip(header,line))
        # Append videos object to list
        data_dicts.append(Video.from_dict(data_dict))
    return data_dicts


def get_pages(country_code, api_key, next_page_token="&"):
    country_data_dict = []

    # Because the API uses page tokens (which are literally just the same function of numbers everywhere) it is much
    # more inconvenient to iterate over pages, but that is what is done here.
    while next_page_token is not None:
        # A page of data i.e. a list of videos and all needed data

        video_data_page = api_request(next_page_token, country_code, api_key)

        # Get the next page token and build a string which can be injected into the request with it, unless it's None,
        # then let the whole thing be None so that the loop ends after this cycle
        next_page_token = video_data_page.get("nextPageToken", None)
        next_page_token = f"&pageToken={next_page_token}&" if next_page_token is not None else next_page_token

        # Get all of the items as a list and dictionary and let get_videos return the needed features
        items = video_data_page.get('items', [])
        videos_data_dict = get_videos(items,country_code)
        country_data_dict  +=  videos_data_dict

    return country_data_dict


def get_data(country_codes:List, api_key):
    # You can iterate over country code in this function if you want
    data_list = []
    for code in country_codes:
        trending_data_dict = get_pages(code, api_key)
        data_list.extend(trending_data_dict)

    return data_list

if __name__ == "__main__":
    # Load .env
    load_dotenv()
    api_key = os.getenv("YOUTUBE_API_KEY")
    country_code = COUNTRY_CODES

    youtube_trending_data = get_data(country_code, api_key)

    for data in youtube_trending_data:
        print(json.dumps(data.__dict__, default=str,  indent=2))
