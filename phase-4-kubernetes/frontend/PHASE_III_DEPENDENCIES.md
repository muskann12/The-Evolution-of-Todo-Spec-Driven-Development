# Phase III: AI Chatbot - Frontend Dependencies

## Installed Packages

### Chat UI Dependencies

**react-markdown** (v9.0.2)
- Purpose: Render markdown in AI responses
- Why: AI responses may contain formatted text (bold, italics, lists, links)
- Usage: Wrap AI response text to display rich formatting
- Docs: https://github.com/remarkjs/react-markdown

**remark-gfm** (v4.0.1)
- Purpose: GitHub Flavored Markdown support
- Why: Enables tables, strikethrough, task lists, and autolinks
- Usage: Plugin for react-markdown
- Docs: https://github.com/remarkjs/remark-gfm

### Existing Dependencies (Already Installed)

These packages are already in the project and will be used for chat:

**Next.js 16.1.1**
- App Router for /chat page routing
- Server and client components
- Already installed ✅

**React 19.2.3**
- Component framework for chat UI
- Already installed ✅

**Tailwind CSS 3.4.19**
- Utility-first CSS for styling chat interface
- Already installed ✅

**@tanstack/react-query 5.90.16**
- Data fetching and caching (optional for chat)
- Already installed ✅

**lucide-react 0.562.0**
- Icons for send button, loading spinner, etc.
- Already installed ✅

## Why These Packages?

### react-markdown + remark-gfm
The AI assistant responses from the backend may include:
- **Bold** and *italic* text
- Lists (ordered and unordered)
- Links
- Code blocks
- Tables (with remark-gfm)
- Task lists (with remark-gfm)

Example AI response:
```
I'll create that task for you. ✅

**Created:** "Buy groceries"
- **Priority:** Medium
- **Status:** Ready

Would you like to:
1. Set a due date?
2. Add tags?
3. Change priority?
```

With react-markdown, this will render beautifully with proper formatting.

### Why NOT Install OpenAI SDK?

**We don't need the OpenAI JavaScript SDK on the frontend because:**
1. All OpenAI integration is handled by the backend (backend/app/ai/agent.py)
2. Frontend only needs to send messages to POST /api/chat/message
3. Backend returns plain text responses
4. This keeps API keys secure (never exposed to client)
5. Simpler architecture - single point of OpenAI integration

## Installation Commands

```bash
# Navigate to frontend directory
cd frontend

# Install existing dependencies (if not done)
npm install

# Install Phase III chat dependencies
npm install react-markdown remark-gfm
```

## Verification

After installation, verify packages are in package.json:

```bash
# Check package.json
cat package.json | grep "react-markdown"
# Expected: "react-markdown": "^9.0.2"

cat package.json | grep "remark-gfm"
# Expected: "remark-gfm": "^4.0.1"
```

Or check node_modules:

```bash
ls node_modules | grep react-markdown
# Expected: react-markdown

ls node_modules | grep remark-gfm
# Expected: remark-gfm
```

## Next Steps

With dependencies installed, we can now:
1. Create chat page at `app/chat/page.tsx`
2. Build chat UI components in `components/features/chat/`
3. Integrate with backend API at `/api/chat/message`
4. Test end-to-end chat flow

## Usage Example

```tsx
// components/features/chat/ChatMessage.tsx
'use client'

import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

export function ChatMessage({ content }: { content: string }) {
  return (
    <div className="prose">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {content}
      </ReactMarkdown>
    </div>
  )
}
```

## Cost & Bundle Size

**react-markdown:** ~50KB (gzipped)
**remark-gfm:** ~10KB (gzipped)

**Total added:** ~60KB to frontend bundle

This is acceptable for the enhanced UX of formatted AI responses.

## Alternative Considered

**Why not use a pre-built chat UI library?**
- Most chat libraries are opinionated and hard to customize
- Building custom UI with Tailwind gives us full control
- Simple chat interface doesn't require heavy library
- react-markdown is lightweight and focused

**Why not OpenAI ChatGPT widget?**
- Requires OpenAI API key on frontend (security risk)
- Less customizable for our specific use case
- We already have complete backend integration
- Our backend handles MCP tools and task management

---

**Phase III - AI-FRONT-001: Install Chat Dependencies - COMPLETE** ✅

**Date:** 2026-01-14
**Status:** Complete
**Next Task:** AI-FRONT-002 - Create Chat Page and Components
