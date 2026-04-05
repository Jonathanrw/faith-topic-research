import json
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def get_youtube_credentials() -> Credentials:
    token_json = os.getenv("YOUTUBE_TOKEN_JSON", "").strip()

    if not token_json:
        raise RuntimeError("Missing YOUTUBE_TOKEN_JSON secret.")

    info = json.loads(token_json)
    creds = Credentials.from_authorized_user_info(info, YOUTUBE_SCOPES)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    if not creds.valid:
        raise RuntimeError("YouTube OAuth credentials are invalid.")

    return creds
