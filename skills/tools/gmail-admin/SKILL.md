---
id: gmail-admin
name: gmail-admin
category: tools
tags:
  - gmail
  - google-cloud
  - api
goals:
  - "Automated Gmail administration using Gmail API and Google Cloud SDK."
authors:
  - Brahyan Belalcazar
---

# Gmail Administration Setup

## Overview

This skill enables automated Gmail administration for iberi22@gmail.com using the Gmail API and Google Cloud SDK.

## Prerequisites

- GCP CLI authenticated with iberi22@gmail.com
- Gmail API enabled in Google Cloud Console
- OAuth 2.0 credentials (client_id + client_secret)

## Setup Steps

### 1. Enable Gmail API

```bash
gcloud services enable gmail.googleapis.com
```

### 2. Create OAuth 2.0 Credentials

Since this is a personal Gmail account (not Google Workspace), you need:

1. Go to: https://console.cloud.google.com/apis/credentials
2. Select project: `saber-proactivo-2025`
3. Create "OAuth client ID" for Desktop app
4. Download the JSON file
5. Save as `gmail-oauth2.json` in a secure location

### 3. Get Authorization Code

```bash
# Using gcloud to get user credentials
gcloud auth application-default login
```

Or manually:
1. Visit: https://accounts.google.com/o/oauth2/auth?client_id=YOUR_CLIENT_ID&redirect_uri=urn:ietf:wg:oauth:2.0:oob&response_type=code&scope=https://www.googleapis.com/auth/gmail.modify
2. Copy the authorization code

### 4. Exchange for Refresh Token

```bash
curl -X POST https://oauth2.googleapis.com/token \
  -d "code=AUTHORIZATION_CODE" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "redirect_uri=urn:ietf:wg:oauth:2.0:oob" \
  -d "grant_type=authorization_code"
```

Response:
```json
{
  "refresh_token": "1//0xxx...",
  "access_token": "ya29.xxx",
  "expires_in": 3599,
  "token_type": "Bearer"
}
```

### 5. Store Credentials Securely

Save refresh token to environment or secure storage:
```bash
export GMAIL_REFRESH_TOKEN="1//0xxx..."
export GMAIL_CLIENT_ID="xxx.apps.googleusercontent.com"
export GMAIL_CLIENT_SECRET="GOCSPX-xxx"
```

## Gmail API Operations

### Read Emails
```bash
curl -X GET "https://gmail.googleapis.com/gmail/v1/users/me/messages" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

### Send Email
```bash
curl -X POST "https://gmail.googleapis.com/gmail/v1/users/me/messages/send" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"raw": "BASE64URL_ENCODED_MESSAGE"}'
```

### Manage Labels
```bash
# List labels
curl -X GET "https://gmail.googleapis.com/gmail/v1/users/me/labels" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

## Agent Integration

The agent can use these tools for Gmail operations:
- Read incoming emails
- Send notifications
- Manage labels/filters
- Archive old emails
- Generate reports

## Security Notes

- Never commit tokens to git
- Use environment variables or secret manager
- Rotate tokens periodically
- Monitor for unauthorized access
