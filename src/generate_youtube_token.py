import json
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def main() -> None:
    client_secret_path = Path("client_secret.json")

    if not client_secret_path.exists():
        raise FileNotFoundError("Put your downloaded OAuth client file here as client_secret.json")

    flow = InstalledAppFlow.from_client_secrets_file(
        str(client_secret_path),
        SCOPES,
    )

    creds = flow.run_local_server(port=0)

    token_info = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes,
    }

    print(json.dumps(token_info, indent=2))
    Path("token.json").write_text(json.dumps(token_info, indent=2), encoding="utf-8")
    print("Saved token.json")
