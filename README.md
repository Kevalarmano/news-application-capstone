# News Application (Django Capstone)

## Overview
This project is a Django News Application with:
- Custom user model with roles: Reader, Editor, Journalist
- Publisher and Article models
- Editor approval workflow for articles
- Login/logout using Django auth
- REST-style JSON API endpoint returning approved articles based on a reader's subscriptions
- Automated tests for the API

## Setup (Local or Codespaces)

### 1) Create a virtual environment (recommended)
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate
