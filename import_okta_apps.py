import json
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

OKTA_NEW_ORG_URL = os.getenv("OKTA_NEW_ORG_URL") or os.getenv("OKTA_ORG_URL")
OKTA_NEW_API_TOKEN = os.getenv("OKTA_NEW_API_TOKEN") or os.getenv("OKTA_API_TOKEN")
TARGET_APPS_ENV = os.getenv("TARGET_APPS", "")

# Convert comma-separated string to a cleaned list of lowercased target names
TARGET_APPS = [app.strip().lower() for app in TARGET_APPS_ENV.split(",") if app.strip()]

CONFIG_DIR = "okta_app_configs"

HEADERS = {
    "Authorization": f"SSWS {OKTA_NEW_API_TOKEN}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

READ_ONLY_FIELDS = [
    "id", "status", "created", "lastUpdated", "last_updated",
    "_links", "embedded", "credentials"
]


def clean_payload_for_import(app_dict):
    """Remove read-only fields and old tenant metadata prior to POSTing."""
    payload = app_dict.copy()
    for field in READ_ONLY_FIELDS:
        payload.pop(field, None)
    return payload


def create_app_in_okta(payload):
    """POST new application payload to Okta API."""
    url = f"{OKTA_NEW_ORG_URL.rstrip('/')}/api/v1/apps"
    return requests.post(url, headers=HEADERS, json=payload)


def main():
    if not OKTA_NEW_ORG_URL or not OKTA_NEW_API_TOKEN:
        print("Error: Missing OKTA_NEW_ORG_URL or OKTA_NEW_API_TOKEN environment variables.")
        sys.exit(1)

    if not os.path.exists(CONFIG_DIR):
        print(f"Error: Directory '{CONFIG_DIR}' not found. Run the export script first.")
        sys.exit(1)

    files = [f for f in os.listdir(CONFIG_DIR) if f.endswith("_config.json")]
    if not files:
        print(f"No configuration files found in ./{CONFIG_DIR}/")
        sys.exit(0)

    print(f"Targeting new Okta org: {OKTA_NEW_ORG_URL}")
    if TARGET_APPS:
        print(f"Filtering for target apps: {', '.join(TARGET_APPS)}\n")
    else:
        print("No TARGET_APPS filter specified; importing all configs in folder.\n")

    for filename in files:
        filepath = os.path.join(CONFIG_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            raw_config = json.load(f)

        app_label = raw_config.get("label", filename)

        # Apply target filter if TARGET_APPS is defined
        if TARGET_APPS and not any(target in app_label.lower() for target in TARGET_APPS):
            print(f"  ➜ Skipping '{app_label}' (does not match TARGET_APPS)")
            continue

        payload = clean_payload_for_import(raw_config)

        print(f"Creating '{app_label}'...")
        response = create_app_in_okta(payload)

        if response.status_code in [200, 201]:
            new_app = response.json()
            print(f"  ✓ Success! Created ID: {new_app.get('id')} (Status: {new_app.get('status')})\n")
        else:
            print(f"  ✗ Failed ({response.status_code}): {response.text}\n")


if __name__ == "__main__":
    main()
