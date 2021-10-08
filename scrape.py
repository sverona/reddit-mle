import json
import sys
from time import sleep

import requests as r
import pandas as pd


def request(url, params=None):
    if not params:
        params = {}

    header = {'User-agent': 'threads-api 0.0'}
    res = r.get(url, headers=header, params=params)
    sleep(1.2)

    if res.status_code == 200:
        return json.loads(res.text.encode("latin-1"))
    else:
        print(res.status_code)
        sys.exit(1)


def follow_thread(comment, parent, processor=None):
    if not processor:
        def identity(comment, parent):
            return comment
        processor = identity

    if comment["data"].get("replies") and comment["data"]["replies"]["data"].get("children"):
        for reply in comment["data"]["replies"]["data"]["children"]:
            if reply["kind"] == "t1":
                print(follow_thread(reply, comment, processor))

    return processor(comment, parent)


data = []


def add_to_data(comment, parent):
    if comment["kind"] == "t1":
        if parent is None:
            parent_id = None
        else:
            parent_id = parent["data"]["id"]
        row = [comment["data"]["id"], parent_id, comment["data"]["depth"], comment["data"]["subreddit"], comment["data"]["created"], comment["data"]["ups"]]

        data.append(row)
        return row


def popular_subreddits(limit):
    res = request("https://reddit.com/subreddits/default.json", {"limit": limit})
    return [sub["data"]["display_name"] for sub in res["data"]["children"]]


SUBS_TO_FETCH = 100
POSTS_PER_SUB_TO_FETCH = 100

for sub in popular_subreddits(SUBS_TO_FETCH):
    these_top_posts = request(f"https://reddit.com/r/{sub}/top.json", {"t": "all", "limit": POSTS_PER_SUB_TO_FETCH})

    for post in these_top_posts["data"]["children"]:
        post_id = post["data"]["id"]
        [post, comments] = request(f"https://reddit.com/r/{sub}/comments/{post_id}.json", {"sort": "top"})

        for comment in comments["data"]["children"][:10]:
            print(follow_thread(comment, None, add_to_data))

df = pd.DataFrame(data, columns=['id', 'parent_id', 'depth', 'subreddit', 'created', 'ups'])

df.to_csv("./comments-data.csv")
