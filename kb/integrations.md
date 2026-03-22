# Integrations & Webhooks

**doc_id: KB-010**

## Available Integrations

| Integration | Purpose | Setup |
|------------|---------|-------|
| Slack | Receive notifications | Settings → Integrations → Slack |
| Zapier | Automate workflows | Use our Zapier app |
| GitHub | Link commits to resources | Settings → Integrations → GitHub |
| Stripe | Payment processing (built-in) | Automatic |
| Google SSO | Single sign-on | Settings → Security → SSO |

## Setting Up Webhooks

1. Go to **Settings → Developer → Webhooks → Add Endpoint**.
2. Enter your HTTPS endpoint URL.
3. Select events to subscribe to (e.g., `resource.created`, `billing.failed`).
4. Save — we'll send a test event immediately.

## Webhook Payload Format

```json
{
  "event": "billing.failed",
  "timestamp": "2024-06-15T10:30:00Z",
  "data": {
    "error_code": "E102",
    "amount": 29.00,
    "currency": "USD"
  }
}
```

## Webhook Security

- All webhooks include a `X-Signature` header (HMAC-SHA256).
- Verify the signature using your webhook secret from the dashboard.
- Replay protection: reject events with timestamps older than 5 minutes.

## Troubleshooting Webhooks

- **Not receiving webhooks**: Check your server's firewall allows inbound HTTPS.
- **Signature mismatch**: Ensure you're using the raw request body (not parsed JSON) for verification.
- **Delivery failures**: We retry 3 times with exponential backoff. Check **Settings → Developer → Webhooks → Delivery Logs**.
