# Billing & Payment Failures

**doc_id: KB-002**

## Common Payment Error Codes

| Code | Meaning | Resolution |
|------|---------|-----------|
| **E101** | Card declined by issuer | Contact your bank or use a different card |
| **E102** | Insufficient funds or credit limit reached | Add funds or increase credit limit with your bank; retry after 24 hours |
| **E103** | Card expired | Update card details under **Billing → Payment Method** |
| **E104** | Invalid CVV/CVC | Re-enter card details carefully |
| **E105** | Billing address mismatch | Ensure billing address matches what's on file with your bank |
| **E110** | Payment gateway timeout | Retry after 5 minutes; if persistent, contact support |

## Troubleshooting Error E102 (Insufficient Funds / Limit Reached)

Error E102 occurs when the card issuer declines the transaction due to insufficient funds or a reached credit limit. Steps to resolve:

1. Verify available balance/credit with your bank.
2. Wait 24 hours — some limits reset daily.
3. Try a different payment method (different card or PayPal).
4. If your account is on an annual plan, consider switching to monthly to reduce single-transaction size.
5. Contact your bank to temporarily raise your limit.
6. If none of the above work, create a support ticket for manual billing assistance.

## Updating Payment Method

1. Go to **Billing → Payment Method → Update Card**.
2. Enter new card details and save.
3. Retry any failed invoice from **Billing → Invoice History**.

## Invoice & Receipts

- All invoices are emailed automatically and available under **Billing → Invoice History**.
- Receipts in PDF format can be downloaded any time.

## Subscription Plans

- **Starter**: $9/month — up to 3 users
- **Pro**: $29/month — up to 20 users
- **Enterprise**: Custom pricing — unlimited users + SLA
