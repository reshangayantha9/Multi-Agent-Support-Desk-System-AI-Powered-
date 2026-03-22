# Known Issues

**doc_id: KB-006**

## Active Issues

### [P1] Dashboard loading slowly for large datasets — Investigating
- **Affects**: Pro and Enterprise users with >10,000 records
- **Workaround**: Use date filters to limit dataset size; pagination available
- **ETA**: Fix targeted for next release (v2.4.1)

### [P2] Email notifications delayed during peak hours
- **Affects**: All users
- **Details**: Emails may be delayed up to 30 minutes between 9 AM–11 AM UTC
- **Workaround**: Check in-app notifications for real-time updates

### [P3] Export to CSV fails for special characters in field names
- **Affects**: Users with non-ASCII characters in custom field names
- **Workaround**: Rename fields to ASCII-only characters before exporting
- **ETA**: v2.4.2

## Recently Resolved Issues

### [RESOLVED] OAuth login failure for Google accounts — Fixed v2.4.0
- Resolved on 2024-06-10. Update to latest version to apply fix.

### [RESOLVED] E102 payment errors on Visa debit cards — Fixed v2.3.9
- An integration issue with Visa debit cards caused false E102 errors. Resolved. If still seeing E102, see the Billing guide for genuine E102 troubleshooting steps.

## How to Report a New Issue

If you're experiencing something not listed here:
1. Check our **Status Page**: https://status.example.com
2. If the issue persists, create a support ticket with:
   - Steps to reproduce
   - Screenshot or error message
   - Browser/OS version (if applicable)
