# Okta Application Configuration Exporter & Importer

A Python-based utility using the official Okta SDK to backup, export, and migrate application configurations (including GitLab, Jenkins, and Mealie.io) between Okta tenants.

---

## Features

- Automated Export: Extracts application configurations via the official Okta Python SDK.
- Environment Isolation: Uses python-dotenv for safe local credential management.
- Pydantic / SDK Compatible: Safely serializes Okta application models across SDK versions.
- Tenant Import Support: Cleans read-only metadata and provisions exported apps into a target Okta tenant.

---

## Project Structure
```text
.
├── fetch_okta_app_config.py  # Script to export app configs from source tenant
├── import_okta_apps.py       # Script to import app configs into target tenant
├── requirements.txt          # Python package dependencies
├── .env.example              # Template for environment variables
├── .gitignore                # Protects secrets and output folders from Git
└── README.md                 # Project documentation
```
---

## Prerequisites

- Python: 3.10 or higher
- Okta Tenant Access: Read/Write API Token with Admin privileges
- Target Applications: GitLab, Jenkins, Mealie.io (or custom target apps)

---

## Getting Started

### 1. Clone the Repository & Set Up Virtual Environment

git clone <your-repository-url>
cd <your-repository-folder>

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows (PowerShell):
# .\venv\Scripts\Activate.ps1

### 2. Install Dependencies

pip install -r requirements.txt

### 3. Configure Environment Variables

Copy .env.example to create your local .env file:

cp .env.example .env

Open .env and fill in your Okta domain and API token, and optional target filter:

# Source Okta Tenant
OKTA_ORG_URL=https://dev-123456.okta.com
OKTA_API_TOKEN=00your_source_api_token_here

# Target Okta Tenant (Required only for import script)
OKTA_NEW_ORG_URL=https://dev-999999.okta.com
OKTA_NEW_API_TOKEN=00your_target_api_token_here

# Optional: Filter specific apps during import (comma-separated)
TARGET_APPS=gitlab,jenkins,mealie

Note: Use the primary Okta org domain (https://dev-XXXXXX.okta.com), not the -admin console URL.

---

## Usage

### 1. Export Application Configurations

Run fetch_okta_app_config.py to extract target app configurations:

python fetch_okta_app_config.py

Output Directory: Creates a okta_app_configs/ folder containing JSON files for matched apps (e.g., gitlab_config.json, jenkins_config.json, mealie.io_config.json).

---

### 2. Import Configurations to a New Tenant

To provision the exported application configurations into a secondary or target Okta trial tenant:

1. Ensure OKTA_NEW_ORG_URL and OKTA_NEW_API_TOKEN are set in .env.
2. Run the import script:

python import_okta_apps.py

Process: Cleans read-only Okta identifiers (id, created, status) and POSTs the cleaned app payloads to the new tenant.

---

## Post-Migration Steps

After importing applications to a new Okta tenant:

1. Re-assign Users & Groups: Group GUIDs differ between tenants and must be reassigned in the new Admin Console.
2. Update ACS / Redirect URIs: If your app URLs changed, update redirect URIs under Applications > [App Name] > General / Sign On.
3. Update Certificates (SAML): For SAML apps (e.g., Jenkins), download the newly generated SAML IdP metadata / x509 certificate from the target Okta tenant and upload it to your target application.

