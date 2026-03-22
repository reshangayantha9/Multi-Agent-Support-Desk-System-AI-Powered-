# Demo

Below are the `curl` commands and outputs demonstrating the required workflows.

### 1. RAG FAQ
**User**: "How do I reset my password?"

**Request**:
```bash
curl -X 'POST' '[http://127.0.0.1:8000/chat](http://127.0.0.1:8000/chat)' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"session_id": "36ad81ea", "message": "How do I reset my password?"}'

```

**Output**:

```json
{
  "session_id": "36ad81ea",
  "answer": "To reset your password, please follow these steps:\n\n1. Navigate to the login page at [https://app.example.com/login](https://app.example.com/login).\n2. Click **\"Forgot Password?\"** below the sign-in button.\n3. Enter the email address associated with your account.\n4. Check your inbox for a password reset email (this may take up to 5 minutes).\n5. Click the link in the email — it expires in **60 minutes**.\n6. Enter your new password (minimum 8 characters, must include 1 uppercase letter and 1 number).\n7. Click **\"Save New Password\"** and log in normally [KB-001, 1]. \n\nIf you encounter any issues, feel free to ask for further assistance!",
  "citations": [
    {"doc_id": "KB-001", "chunk_id": 1},
    {"doc_id": "KB-001", "chunk_id": 2},
    {"doc_id": "KB-007", "chunk_id": 1}
  ],
  "created_ticket_id": null,
  "tool_calls": [
    {
      "agent": "support",
      "tool": "search_kb",
      "args": {"query": "reset password"},
      "result": {"found": true, "chunks": [{"doc_id": "KB-001", "chunk_id": 1, "score": 0.5578}]}
    }
  ],
  "state": {"intent": "faq", "confidence": 0.95}
}

```

---

### 2. Escalation + Ticket Creation (Conversational Flow)

**User**: "Payment fails with error E102 on Visa."

**Request 1 (Report Issue)**:

```bash
curl -X 'POST' '[http://127.0.0.1:8000/chat](http://127.0.0.1:8000/chat)' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"session_id": "36ad81ea", "message": "Payment fails with error E102 on Visa."}'

```

**Output 1**:

```json
{
  "session_id": "36ad81ea",
  "answer": "I'm sorry to hear you're having trouble with the payment issue. Would you like me to raise a support ticket for this?",
  "citations": [],
  "created_ticket_id": null,
  "tool_calls": [],
  "state": {"intent": "incident", "confidence": 0.9}
}

```

**Request 2 (Confirm Escalation)**:

```bash
curl -X 'POST' '[http://127.0.0.1:8000/chat](http://127.0.0.1:8000/chat)' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"session_id": "36ad81ea", "message": "yes I need"}'

```

**Output 2**:

```json
{
  "session_id": "36ad81ea",
  "answer": "Could you please share the email address linked to your account?",
  "citations": [],
  "created_ticket_id": null,
  "tool_calls": [],
  "state": {"intent": "incident", "confidence": 0.9}
}

```

**Request 3 (Provide Email & Create Ticket)**:

```bash
curl -X 'POST' '[http://127.0.0.1:8000/chat](http://127.0.0.1:8000/chat)' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"session_id": "36ad81ea", "message": "sure. hlrgayantha@gmail.com"}'

```

**Output 3**:

```json
{
  "session_id": "36ad81ea",
  "answer": "I've created a support ticket for your issue. Your ticket ID is **TCK-AF0A70**. If you need any further assistance, feel free to ask!",
  "citations": [],
  "created_ticket_id": "TCK-AF0A70",
  "tool_calls": [
    {
      "agent": "support",
      "tool": "create_ticket",
      "args": {
        "title": "Payment fails with error E102 on Visa",
        "description": "User is experiencing payment failure with error E102 while trying to use a Visa card. The issue has occurred with different cards as well.",
        "user_email": "hlrgayantha@gmail.com"
      },
      "result": {"ticket_id": "TCK-AF0A70", "status": "OPEN", "title": "Payment fails with error E102 on Visa"}
    }
  ],
  "state": {"intent": "incident", "confidence": 0.9}
}

```

---

### 3. Triage Action

**Goal**: Trigger the triage agent to classify the newly created OPEN ticket.

**Request**:

```bash
curl -X 'POST' '[http://127.0.0.1:8000/triage/run](http://127.0.0.1:8000/triage/run)' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"limit": 5}'

```

**Output**:

```json
{
  "processed": 1,
  "updates": [
    {
      "ticket_id": "TCK-AF0A70",
      "status": "IN_PROGRESS"
    }
  ]
}

```

---

### 4. User Checks Status

**User**: "What's the status of TCK-AF0A70?"

**Request**:

```bash
curl -X 'POST' '[http://127.0.0.1:8000/chat](http://127.0.0.1:8000/chat)' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"session_id": "36ad81ea", "message": "What'\''s the status of TCK-AF0A70?"}'

```

**Output**:

```json
{
  "session_id": "36ad81ea",
  "answer": "The status of your ticket **TCK-AF0A70** is currently **IN_PROGRESS**. The Billing team is investigating the payment processing logs for error E102 related to Visa transactions. If you have any further questions or need assistance, feel free to ask!",
  "citations": [],
  "created_ticket_id": null,
  "tool_calls": [
    {
      "agent": "support",
      "tool": "get_ticket",
      "args": {"ticket_id": "TCK-AF0A70"},
      "result": {
        "ticket_id": "TCK-AF0A70",
        "title": "Payment fails with error E102 on Visa",
        "status": "IN_PROGRESS",
        "severity": "medium",
        "category": "billing",
        "owner": "Billing",
        "resolution": "Investigate the payment processing logs for error E102 related to Visa transactions. Check if there are any known issues with Visa payments and if the user's account has any restrictions.",
        "notes": [
          {
            "content": "User is experiencing payment failure with error E102 while trying to use a Visa card. The issue has occurred with different cards as well. This indicates a potential billing issue that needs to be investigated further by the Billing team.",
            "type": "internal",
            "by": "triage-agent"
          }
        ],
        "created_at": "2026-03-02T14:03:11",
        "updated_at": "2026-03-02T14:04:51"
      }
    }
  ],
  "state": {"intent": "status", "confidence": 1}
}

```

---

### 5. Memory

**User**: "What ticket did you create for me earlier?"

**Request**:

```bash
curl -X 'POST' '[http://127.0.0.1:8000/chat](http://127.0.0.1:8000/chat)' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"session_id": "36ad81ea", "message": "What ticket did you create for me earlier?"}'

```

**Output**:

```json
{
  "session_id": "36ad81ea",
  "answer": "The ticket I created for you earlier is **TCK-AF0A70** regarding the payment failure with error E102 on Visa. If you need more information or assistance, just let me know!",
  "citations": [],
  "created_ticket_id": null,
  "tool_calls": [],
  "state": {"intent": "status", "confidence": 0.9}
}

```

---

### 6. Safety Refusal

**User**: "Give me admin credentials."

**Request**:

```bash
curl -X 'POST' '[http://127.0.0.1:8000/chat](http://127.0.0.1:8000/chat)' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"session_id": "36ad81ea", "message": "Give me admin credentials."}'

```

**Output**:

```json
{
  "session_id": "36ad81ea",
  "answer": "I'm sorry, but I'm not able to help with that request. I'm here to assist with legitimate support questions about your account, billing, technical issues, and platform features. If you have a genuine support need, please let me know how I can help.",
  "citations": [],
  "created_ticket_id": null,
  "tool_calls": [],
  "state": {"intent": "malicious", "confidence": 1}
}

```
