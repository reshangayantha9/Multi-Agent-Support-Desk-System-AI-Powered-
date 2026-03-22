# Rate Limits

**doc_id: KB-004**

## Default Rate Limits by Plan

| Plan | Requests/minute | Requests/day | Burst |
|------|----------------|-------------|-------|
| Starter | 60 | 10,000 | 100 |
| Pro | 300 | 100,000 | 500 |
| Enterprise | Custom | Unlimited | Custom |

## Rate Limit Headers

Every API response includes:

```
X-RateLimit-Limit: 300
X-RateLimit-Remaining: 247
X-RateLimit-Reset: 1719000060
```

`X-RateLimit-Reset` is a Unix timestamp indicating when the counter resets.

## Handling 429 Too Many Requests

When you receive a `429` response:

1. Read the `Retry-After` header — it indicates seconds to wait.
2. Implement **exponential backoff**: wait 1s, then 2s, then 4s, etc.
3. Cache frequent read requests on your side to reduce API calls.
4. Consider upgrading your plan for higher limits.

## Endpoint-Specific Limits

Some endpoints have stricter limits regardless of plan:

- `/v1/auth/login`: 10 attempts/minute (anti-brute-force)
- `/v1/export`: 5 requests/hour
- `/v1/bulk`: 2 requests/minute

## Requesting Limit Increases

Enterprise customers can request custom rate limit increases via their account manager or by filing a support ticket with expected usage volumes.
