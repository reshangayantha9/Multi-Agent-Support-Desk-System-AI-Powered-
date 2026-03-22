# API Keys & Authentication

**doc_id: KB-003**

## Generating an API Key

1. Log into your account and navigate to **Settings → Developer → API Keys**.
2. Click **"Create New Key"**.
3. Give the key a descriptive name (e.g., "Production Server").
4. Copy and securely store the key — it is shown only once.
5. Assign scopes: `read`, `write`, or `admin`.

## Using Your API Key

Include the key in the `Authorization` header:

```
Authorization: Bearer YOUR_API_KEY
```

Example request:
```bash
curl -H "Authorization: Bearer sk_live_xxxxx" https://api.example.com/v1/resource
```

## API Key Security Best Practices

- Never commit keys to source control (use `.env` files or secret managers).
- Rotate keys every 90 days.
- Use the minimum required scope.
- Delete unused keys immediately.

## Rotating / Revoking a Key

1. Go to **Settings → Developer → API Keys**.
2. Click the ⚙️ icon next to the key.
3. Select **Revoke** to immediately invalidate it, or **Rotate** to generate a new one (old key remains valid for 24 hours).

## OAuth 2.0 Integration

We support OAuth 2.0 Authorization Code flow for third-party integrations. Client ID and Client Secret are available under **Settings → Developer → OAuth Apps**.

## Common Auth Errors

| Code | Meaning |
|------|---------|
| 401 Unauthorized | Missing or invalid API key |
| 403 Forbidden | Valid key but insufficient scope |
| 429 Too Many Requests | Rate limit exceeded (see Rate Limits doc) |
