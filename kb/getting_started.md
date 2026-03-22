# Getting Started Guide

**doc_id: KB-009**

## Quick Start (5 minutes)

### 1. Create Your Account
- Sign up at https://app.example.com/signup
- Verify your email address

### 2. Set Up Your Workspace
- Choose a workspace name (used in your URL: `yourworkspace.example.com`)
- Invite team members under **Settings → Team → Invite**

### 3. Generate Your First API Key
- Go to **Settings → Developer → API Keys → Create New Key**
- Store it safely — shown only once!

### 4. Make Your First API Call
```bash
curl -H "Authorization: Bearer YOUR_KEY" \
     https://api.example.com/v1/health
```
Expected response: `{"status": "ok"}`

## Core Concepts

- **Workspace**: Your isolated environment. All data is scoped to a workspace.
- **Resources**: The main objects you create and manage via the API.
- **Webhooks**: Real-time notifications to your server when events occur.

## Next Steps

- Explore the full API reference at https://docs.example.com
- Set up webhooks under **Settings → Developer → Webhooks**
- Join our community Slack: https://slack.example.com

## Getting Help

- In-app chat support (this chat!)
- Documentation: https://docs.example.com
- Community forum: https://community.example.com
- Status page: https://status.example.com
