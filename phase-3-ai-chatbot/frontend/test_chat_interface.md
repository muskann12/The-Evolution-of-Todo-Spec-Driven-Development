# Phase III - Chat Interface Testing Guide

## Overview
This document provides a comprehensive manual testing guide for the AI chatbot interface (AI-FRONT-002).

**Test Date:** 2026-01-14
**Component:** Chat Page (`app/(dashboard)/chat/page.tsx`)
**Backend Endpoint:** `POST /api/chat/message`

---

## Prerequisites

### 1. Backend Server Running
```bash
$ curl http://localhost:8000/health
{"status":"healthy","service":"todo-api"}
```

### 2. Frontend Server Running
```bash
$ curl -I http://localhost:3000
HTTP/1.1 200 OK
```

### 3. Environment Variables Set
```bash
# Backend .env file must include:
OPENAI_API_KEY=sk-proj-...
DATABASE_URL=postgresql://...
```

### 4. Database Migrated
```bash
cd phase-3-ai-chatbot/backend
alembic upgrade head
# Should show: conversations and messages tables created
```

### 5. Test User Account
Create a test user account:
- Email: test@example.com
- Password: testpassword123
- Register at: http://localhost:3000/signup

---

## Test Cases

### Test Case 1: Chat Page Access (Authentication)

**Objective:** Verify chat page is protected and requires authentication

**Steps:**
1. Open browser in incognito/private mode
2. Navigate to http://localhost:3000/chat
3. Should redirect to /login

**Expected Result:**
- ✅ Redirects to /login page
- ✅ Cannot access chat without authentication

**Status:** [ ]

---

### Test Case 2: Chat Page UI Rendering

**Objective:** Verify chat page renders correctly when authenticated

**Steps:**
1. Login as test user (test@example.com)
2. Navigate to http://localhost:3000/chat
3. Verify page elements

**Expected Result:**
- ✅ KanbanNavbar visible at top
- ✅ Header section displays:
  - Bot icon with purple/blue gradient background
  - Title: "AI Task Assistant"
  - Subtitle: "Ask me to create, update, or manage your tasks"
- ✅ Messages area shows empty state:
  - MessageSquare icon
  - "Start a conversation" heading
  - Example prompts displayed
- ✅ Input form at bottom:
  - Text input with placeholder
  - Send button with icon

**Status:** [ ]

---

### Test Case 3: Send First Message

**Objective:** Verify user can send first message and receive AI response

**Steps:**
1. Login and navigate to /chat
2. Type message: "Create a task to buy groceries"
3. Click Send button (or press Enter)
4. Observe behavior

**Expected Result:**
- ✅ User message appears immediately (optimistic update)
  - Right-aligned
  - Purple/blue gradient background
  - White text
  - Timestamp displayed
- ✅ Loading indicator appears
  - Bot icon with spinning loader
  - "Thinking..." text
- ✅ After ~2-5 seconds, AI response appears
  - Left-aligned
  - Gray background
  - Bot icon
  - Response text rendered with markdown
  - Timestamp displayed
- ✅ Input clears after sending
- ✅ Send button re-enabled
- ✅ Auto-scroll to latest message

**Status:** [ ]

---

### Test Case 4: Markdown Rendering

**Objective:** Verify AI responses render markdown correctly

**Steps:**
1. Send message: "List my tasks"
2. Observe AI response formatting

**Expected Result:**
AI response should include markdown formatting:
- ✅ **Bold** text renders correctly
- ✅ *Italic* text renders correctly
- ✅ Lists (bullets or numbered) display properly
- ✅ Line breaks preserved
- ✅ Emojis display (if used by AI)

**Example AI Response:**
```
Here are your tasks: ✅

**High Priority:**
- Client presentation
- Finish report

**Medium Priority:**
- Buy groceries

Would you like to update any of these?
```

**Status:** [ ]

---

### Test Case 5: Multi-Turn Conversation

**Objective:** Verify conversation continuity across multiple messages

**Steps:**
1. Send message 1: "Create a task to buy groceries"
2. Wait for AI response
3. Send message 2: "Set it to high priority"
4. Wait for AI response
5. Send message 3: "What tasks do I have?"
6. Wait for AI response

**Expected Result:**
- ✅ All messages display in chronological order
- ✅ conversation_id maintained across messages
- ✅ AI remembers context from previous messages
- ✅ Auto-scroll keeps latest message visible
- ✅ No duplicate messages

**Status:** [ ]

---

### Test Case 6: Error Handling - Network Error

**Objective:** Verify error handling when backend is unreachable

**Steps:**
1. Stop backend server (Ctrl+C)
2. In chat, send message: "Create a task"
3. Observe behavior

**Expected Result:**
- ✅ User message appears (optimistic update)
- ✅ Loading indicator appears
- ✅ After timeout, error message displays:
  - Red background
  - Error text: "Failed to send message. Please try again."
- ✅ User message removed (rollback)
- ✅ Input remains enabled
- ✅ User can retry

**Status:** [ ]

---

### Test Case 7: Error Handling - Authentication Error

**Objective:** Verify error handling when JWT token expires

**Steps:**
1. Login and open /chat
2. Wait for JWT token to expire (or manually delete auth cookie)
3. Send message: "Create a task"
4. Observe behavior

**Expected Result:**
- ✅ API call returns 401
- ✅ Redirects to /login automatically
- ✅ User can login again
- ✅ Chat page accessible after re-login

**Status:** [ ]

---

### Test Case 8: Loading State During AI Processing

**Objective:** Verify loading indicator shows during AI processing

**Steps:**
1. Send message: "Create a high priority task for client presentation with description 'prepare slides' and tags 'work' and 'urgent'"
2. Observe loading state

**Expected Result:**
- ✅ Loading indicator appears immediately
- ✅ Spinner animates smoothly
- ✅ "Thinking..." text displayed
- ✅ Input disabled during loading
- ✅ Send button disabled during loading
- ✅ Loading indicator disappears after response

**Status:** [ ]

---

### Test Case 9: Empty Message Prevention

**Objective:** Verify cannot send empty messages

**Steps:**
1. Leave input empty
2. Try to click Send button
3. Try pressing Enter

**Expected Result:**
- ✅ Send button disabled when input empty
- ✅ Enter key does nothing when input empty
- ✅ No API request made

**Status:** [ ]

---

### Test Case 10: Responsive Design

**Objective:** Verify chat page is responsive on different screen sizes

**Steps:**
1. Open chat page
2. Resize browser window to mobile width (375px)
3. Verify layout
4. Resize to tablet width (768px)
5. Verify layout
6. Resize to desktop width (1280px)

**Expected Result:**
- ✅ Mobile (375px):
  - KanbanNavbar adapts
  - Messages stack vertically
  - Input takes full width
  - Readable text size
- ✅ Tablet (768px):
  - Chat container centered
  - Good use of space
- ✅ Desktop (1280px):
  - Chat container max-width (4xl)
  - Centered layout
  - Optimal reading width

**Status:** [ ]

---

### Test Case 11: Auto-Scroll Behavior

**Objective:** Verify auto-scroll keeps latest message visible

**Steps:**
1. Send 20 messages to fill the chat area
2. Observe scroll behavior after each message

**Expected Result:**
- ✅ After each message, view scrolls to bottom
- ✅ Smooth scrolling animation
- ✅ Latest message always visible
- ✅ User can manually scroll up to view history
- ✅ New messages scroll back to bottom

**Status:** [ ]

---

### Test Case 12: Conversation Persistence (Stateless Architecture)

**Objective:** Verify conversations persist across server restarts

**Steps:**
1. Send message: "Create a task to buy groceries"
2. Note the conversation_id (check browser devtools network tab)
3. Stop backend server (Ctrl+C)
4. Restart backend server
5. Refresh frontend page
6. Check if conversation_id is maintained

**Expected Result:**
- ✅ Conversation persisted in database
- ✅ Messages reloaded from database
- ✅ conversation_id maintained
- ✅ Can continue conversation after restart

**Status:** [ ]

---

## Performance Metrics

### Response Time
- **Target:** < 5 seconds per message
- **Actual:** _____ seconds (average)

### Token Usage
- **Target:** < 2000 tokens per message
- **Actual:** _____ tokens (average)

### Bundle Size Impact
- **react-markdown:** ~50KB gzipped
- **remark-gfm:** ~10KB gzipped
- **Total added:** ~60KB

---

## Browser Compatibility

Test on the following browsers:

- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

---

## Accessibility

- [ ] Keyboard navigation works (Tab, Enter)
- [ ] Screen reader compatible (test with NVDA/JAWS)
- [ ] Color contrast meets WCAG AA standards
- [ ] Focus indicators visible

---

## Known Issues

*Document any issues found during testing:*

1. Issue: _______________
   - Steps to reproduce: _______________
   - Expected: _______________
   - Actual: _______________
   - Severity: [ ] Critical [ ] High [ ] Medium [ ] Low
   - Status: [ ] Open [ ] Fixed [ ] Won't Fix

---

## Sign-Off

**Tester:** _______________
**Date:** _______________
**Overall Status:** [ ] Pass [ ] Fail [ ] Blocked
**Notes:** _______________

---

## Next Steps

After all tests pass:
1. Update implementation log with test results
2. Mark AI-FRONT-002 as fully verified
3. Create git commit with changes
4. Move to next task (AI-FRONT-003 or Phase 4)

---

**Generated:** 2026-01-14
**Component:** Phase III Chat Interface
**Version:** 1.0.0
