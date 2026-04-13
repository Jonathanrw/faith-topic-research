import os
import requests
import json

META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")

def post_to_facebook(video_path, caption):
    url = f"https://graph.facebook.com/v19.0/{FACEBOOK_PAGE_ID}/videos"

    files = {
        'file': open(video_path, 'rb')
    }

    data = {
        'description': caption,
        'access_token': META_ACCESS_TOKEN
    }

    response = requests.post(url, files=files, data=data)
    print("Facebook response:", response.json())


def post_to_instagram(video_url, caption):
    # Step 1: Create media container
    create_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media"

    data = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "access_token": META_ACCESS_TOKEN
    }

    res = requests.post(create_url, data=data).json()
    creation_id = res.get("id")

    if not creation_id:
        print("Error creating IG media:", res)
        return

    # Step 2: Publish
    publish_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media_publish"

    publish_res = requests.post(publish_url, data={
        "creation_id": creation_id,
        "access_token": META_ACCESS_TOKEN
    }).json()

    print("Instagram response:", publish_res)
