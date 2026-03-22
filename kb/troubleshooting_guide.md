# Troubleshooting Guide

**doc_id: KB-007**

## General Troubleshooting Steps

1. **Clear cache and cookies** — Most display issues resolve with a hard refresh (`Ctrl+Shift+R` / `Cmd+Shift+R`).
2. **Try incognito mode** — Rules out browser extensions interfering.
3. **Check browser console** — Press F12, look for red errors and share them with support.
4. **Verify your plan** — Some features are plan-restricted.

## Login Issues

- **Can't log in**: Try password reset. If still failing, check if your account email is correct.
- **Account locked**: Wait 30 minutes or contact support for early unlock.
- **2FA not working**: Ensure device clock is synchronized. Use a backup code if needed.

## API / Integration Issues

- **401 errors**: API key may be expired or revoked. Generate a new key.
- **403 errors**: Your key lacks the required scope. Check key settings.
- **500 errors**: Temporary server issue. Retry after 1 minute. Check status page.
- **Timeout errors**: Reduce batch size or implement retry logic with exponential backoff.

## Payment Issues

- Refer to the **Billing & Payment Failures** document for error codes.
- If your card keeps failing despite having funds, contact your bank — they may be blocking the transaction.

## Performance Issues

- **Slow dashboard**: Apply date range filters; reduce number of widgets visible.
- **API calls slow**: Check if you're near rate limits; consider caching responses.

## Data / Sync Issues

- **Data not updating**: Force a page refresh. If real-time sync, check WebSocket connection.
- **Missing records**: Verify filter settings aren't hiding results.

## Escalation

If none of the above resolves your issue, create a support ticket with:
- Exact error message or screenshot
- Steps to reproduce
- Account email and plan type
- Approximate time the issue started
