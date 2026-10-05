import asyncio
import json
import os
import sys
from dotenv import load_dotenv
from okta.client import Client as OktaClient

# Load environment variables from .env file
load_dotenv()

OKTA_ORG_URL = os.getenv("OKTA_ORG_URL")
OKTA_API_TOKEN = os.getenv("OKTA_API_TOKEN")

# Target apps to filter for (lowercased)
TARGET_APPS = ["gitlab", "jenkins", "mealie"]


def validate_env_vars():
    """Verify required environment variables exist."""
    missing = []
    if not OKTA_ORG_URL:
        missing.append("OKTA_ORG_URL")
    if not OKTA_API_TOKEN:
        missing.append("OKTA_API_TOKEN")

    if missing:
        print(f"Error: Missing required environment variable(s): {', '.join(missing)}")
        print("Please check your .env file.")
        sys.exit(1)


def app_to_dict(app):
    """Safely convert Okta SDK application objects to a dict across SDK/Pydantic versions."""
    if hasattr(app, "model_dump"):
        return app.model_dump(mode="json")
    elif hasattr(app, "to_dict"):
        return app.to_dict()
    elif hasattr(app, "as_dict"):
        return app.as_dict()
    else:
        return vars(app)


async def main():
    validate_env_vars()

    # Configure Okta SDK Client
    config = {
        "orgUrl": OKTA_ORG_URL,
        "token": OKTA_API_TOKEN
    }

    client = OktaClient(config)
    output_dir = "okta_app_configs"
    os.makedirs(output_dir, exist_ok=True)

    print(f"Connecting to Okta org: {OKTA_ORG_URL}...")

    # Fetch all applications from Okta
    apps, resp, err = await client.list_applications()

    if err:
        print(f"Error fetching applications from Okta: {err}")
        return

    print(f"Retrieved {len(apps)} applications total.\n")

    matched_count = 0

    for app in apps:
        label = getattr(app, "label", "").lower()

        # Match against target list (GitLab, Jenkins, Mealie)
        if any(target in label for target in TARGET_APPS):
            matched_count += 1
            
            # Safely serialize application object
            app_dict = app_to_dict(app)

            safe_label = getattr(app, "label", "app").replace(" ", "_").lower()
            filename = f"{output_dir}/{safe_label}_config.json"

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(app_dict, f, indent=2, default=str)

            sign_on = getattr(app, "sign_on_mode", "N/A")
            print(f"  ✓ Exported: {app.label} ({sign_on}) -> {filename}")

    if matched_count == 0:
        print("\nNo matching target applications found. Available apps in tenant:")
        for app in apps:
            app_label = getattr(app, "label", "Unknown")
            sign_on = getattr(app, "sign_on_mode", "N/A")
            print(f" - {app_label} (Mode: {sign_on})")
    else:
        print(f"\nDone! Successfully exported {matched_count} configuration(s) to './{output_dir}/'.")


if __name__ == "__main__":
    asyncio.run(main())
