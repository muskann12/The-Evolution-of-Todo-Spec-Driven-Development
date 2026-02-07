# Skill: AI Chat Interface

## Description
Build a modern, responsive chat interface for AI-powered TODO management using Next.js, React, and TypeScript. Create an intuitive conversational UI with message history, typing indicators, and real-time updates.

## When to Use
- Building the frontend chat UI for Phase 3
- Implementing conversational interfaces
- Creating message components and layouts
- Adding chat features (typing indicators, message bubbles, etc.)
- Integrating frontend with AI backend

## Prerequisites
- Next.js 15+ with App Router
- React 18+
- TypeScript
- Tailwind CSS
- React Query for data fetching
- AI chat API endpoint configured

---

## Core Concepts

### Chat Interface Components
1. **ChatContainer** - Main chat layout
2. **MessageList** - Scrollable message history
3. **MessageBubble** - Individual message component
4. **ChatInput** - Message input with send button
5. **TypingIndicator** - Shows when AI is thinking
6. **ConversationList** - Sidebar with chat history

### Key Features
- Real-time message streaming
- Markdown rendering in messages
- Code syntax highlighting
- Task action buttons (create, update, etc.)
- Voice input button
- Conversation management
- Responsive design (mobile/desktop)

---

## Implementation

### 1. Project Structure

```
frontend/src/
├── app/
│   └── chat/
│       ├── page.tsx              # Chat page
│       └── layout.tsx            # Chat layout
├── components/
│   └── chat/
│       ├── ChatContainer.tsx     # Main container
│       ├── MessageList.tsx       # Message list
│       ├── MessageBubble.tsx     # Message component
│       ├── ChatInput.tsx         # Input component
│       ├── TypingIndicator.tsx   # Typing animation
│       ├── ConversationList.tsx  # Sidebar
│       ├── ToolCallDisplay.tsx   # Show tool executions
│       └── VoiceButton.tsx       # Voice input
├── hooks/
│   ├── useChat.ts               # Chat logic
│   ├── useConversations.ts      # Conversation management
│   └── useVoiceInput.ts         # Voice recording
├── lib/
│   ├── chat-api.ts              # API client
│   └── markdown.ts              # Markdown utils
└── types/
    └── chat.ts                  # TypeScript types
```

### 2. TypeScript Types

```typescript
// types/chat.ts
export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  tool_calls?: ToolCall[]
  metadata?: MessageMetadata
}

export interface ToolCall {
  tool: string
  args: Record<string, any>
  result: any
  success: boolean
}

export interface MessageMetadata {
  tokens?: number
  model?: string
  latency?: number
}

export interface Conversation {
  id: number
  title: string
  created_at: string
  updated_at: string
  message_count?: number
}

export interface ChatResponse {
  response: string
  conversation_id: number
  tool_calls: ToolCall[]
}

export interface SendMessageParams {
  message: string
  conversation_id?: number
}
```

### 3. Chat API Client

```typescript
// lib/chat-api.ts
import { Message, Conversation, ChatResponse, SendMessageParams } from '@/types/chat'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export class ChatAPI {
  private static getHeaders(): HeadersInit {
    return {
      'Content-Type': 'application/json',
      // Add auth token from cookies or localStorage
      'Authorization': `Bearer ${this.getAuthToken()}`
    }
  }

  private static getAuthToken(): string {
    // Get from httpOnly cookie or localStorage
    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth_token') || ''
    }
    return ''
  }

  /**
   * Send a message to the AI agent
   */
  static async sendMessage(params: SendMessageParams): Promise<ChatResponse> {
    const response = await fetch(`${API_BASE}/api/chat`, {
      method: 'POST',
      headers: this.getHeaders(),
      credentials: 'include', // Include cookies
      body: JSON.stringify({
        message: params.message,
        conversation_id: params.conversation_id
      })
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({}))
      throw new Error(error.message || 'Failed to send message')
    }

    return response.json()
  }

  /**
   * Get all conversations for the current user
   */
  static async getConversations(): Promise<Conversation[]> {
    const response = await fetch(`${API_BASE}/api/chat/conversations`, {
      headers: this.getHeaders(),
      credentials: 'include'
    })

    if (!response.ok) {
      throw new Error('Failed to fetch conversations')
    }

    return response.json()
  }

  /**
   * Get messages for a specific conversation
   */
  static async getConversationMessages(conversationId: number): Promise<Message[]> {
    const response = await fetch(
      `${API_BASE}/api/chat/conversations/${conversationId}/messages`,
      {
        headers: this.getHeaders(),
        credentials: 'include'
      }
    )

    if (!response.ok) {
      throw new Error('Failed to fetch messages')
    }

    const messages = await response.json()

    // Convert timestamp strings to Date objects
    return messages.map((msg: any) => ({
      ...msg,
      timestamp: new Date(msg.created_at)
    }))
  }

  /**
   * Delete a conversation
   */
  static async deleteConversation(conversationId: number): Promise<void> {
    const response = await fetch(
      `${API_BASE}/api/chat/conversations/${conversationId}`,
      {
        method: 'DELETE',
        headers: this.getHeaders(),
        credentials: 'include'
      }
    )

    if (!response.ok) {
      throw new Error('Failed to delete conversation')
    }
  }

  /**
   * Update conversation title
   */
  static async updateConversationTitle(
    conversationId: number,
    title: string
  ): Promise<void> {
    const response = await fetch(
      `${API_BASE}/api/chat/conversations/${conversationId}`,
      {
        method: 'PATCH',
        headers: this.getHeaders(),
        credentials: 'include',
        body: JSON.stringify({ title })
      }
    )

    if (!response.ok) {
      throw new Error('Failed to update conversation')
    }
  }
}
```

### 4. Chat Hook

```typescript
// hooks/useChat.ts
import { useState, useCallback, useRef, useEffect } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ChatAPI } from '@/lib/chat-api'
import { Message } from '@/types/chat'

export function useChat(conversationId?: number) {
  const [messages, setMessages] = useState<Message[]>([])
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const queryClient = useQueryClient()

  // Load conversation messages
  const { data: loadedMessages, isLoading } = useQuery({
    queryKey: ['conversation', conversationId],
    queryFn: () => conversationId
      ? ChatAPI.getConversationMessages(conversationId)
      : Promise.resolve([]),
    enabled: !!conversationId
  })

  useEffect(() => {
    if (loadedMessages) {
      setMessages(loadedMessages)
    }
  }, [loadedMessages])

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: ChatAPI.sendMessage,
    onSuccess: (data) => {
      // Add assistant message
      const assistantMessage: Message = {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
        tool_calls: data.tool_calls
      }

      setMessages(prev => [...prev, assistantMessage])
      setIsTyping(false)

      // Invalidate conversations to update last message
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
    },
    onError: (error) => {
      console.error('Failed to send message:', error)
      setIsTyping(false)

      // Add error message
      const errorMessage: Message = {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    }
  })

  // Send message
  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return

    // Add user message immediately
    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: content.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setIsTyping(true)

    // Send to backend
    await sendMessageMutation.mutateAsync({
      message: content.trim(),
      conversation_id: conversationId
    })
  }, [conversationId, sendMessageMutation])

  // Scroll to bottom
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, scrollToBottom])

  return {
    messages,
    isTyping,
    isLoading,
    sendMessage,
    messagesEndRef,
    conversationId: conversationId || (messages.length > 0 ? messages[0].id : undefined)
  }
}
```

### 5. Message Bubble Component

```typescript
// components/chat/MessageBubble.tsx
import React from 'react'
import { Message } from '@/types/chat'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { ToolCallDisplay } from './ToolCallDisplay'

interface MessageBubbleProps {
  message: Message
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[80%] ${isUser ? 'order-2' : 'order-1'}`}>
        {/* Avatar */}
        <div className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
          <div className={`
            w-8 h-8 rounded-full flex items-center justify-center text-white font-semibold
            ${isUser ? 'bg-blue-600' : 'bg-purple-600'}
          `}>
            {isUser ? 'U' : 'AI'}
          </div>

          {/* Message Content */}
          <div className={`
            rounded-2xl px-4 py-3 shadow-sm
            ${isUser
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100'
            }
          `}>
            <ReactMarkdown
              className="prose prose-sm dark:prose-invert max-w-none"
              components={{
                code({ node, inline, className, children, ...props }) {
                  const match = /language-(\w+)/.exec(className || '')
                  return !inline && match ? (
                    <SyntaxHighlighter
                      style={vscDarkPlus}
                      language={match[1]}
                      PreTag="div"
                      {...props}
                    >
                      {String(children).replace(/\n$/, '')}
                    </SyntaxHighlighter>
                  ) : (
                    <code className={className} {...props}>
                      {children}
                    </code>
                  )
                }
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
        </div>

        {/* Tool Calls */}
        {message.tool_calls && message.tool_calls.length > 0 && (
          <div className="mt-2 ml-11">
            <ToolCallDisplay toolCalls={message.tool_calls} />
          </div>
        )}

        {/* Timestamp */}
        <div className={`text-xs text-gray-500 mt-1 ${isUser ? 'text-right mr-11' : 'ml-11'}`}>
          {message.timestamp.toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
          })}
        </div>
      </div>
    </div>
  )
}
```

### 6. Tool Call Display

```typescript
// components/chat/ToolCallDisplay.tsx
import React, { useState } from 'react'
import { ToolCall } from '@/types/chat'
import { CheckCircle, XCircle, ChevronDown, ChevronUp } from 'lucide-react'

interface ToolCallDisplayProps {
  toolCalls: ToolCall[]
}

export function ToolCallDisplay({ toolCalls }: ToolCallDisplayProps) {
  const [expanded, setExpanded] = useState(false)

  if (toolCalls.length === 0) return null

  return (
    <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-3 space-y-2">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300 w-full"
      >
        {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        <span>Actions Performed ({toolCalls.length})</span>
      </button>

      {expanded && (
        <div className="space-y-2">
          {toolCalls.map((call, index) => (
            <div
              key={index}
              className="bg-white dark:bg-gray-800 rounded p-2 border border-gray-200 dark:border-gray-700"
            >
              <div className="flex items-center gap-2 mb-1">
                {call.success ? (
                  <CheckCircle size={16} className="text-green-600" />
                ) : (
                  <XCircle size={16} className="text-red-600" />
                )}
                <span className="font-mono text-sm font-semibold">
                  {call.tool}
                </span>
              </div>

              {/* Arguments */}
              <div className="text-xs text-gray-600 dark:text-gray-400 ml-6">
                <div className="font-semibold mb-1">Arguments:</div>
                <pre className="bg-gray-100 dark:bg-gray-900 rounded p-2 overflow-x-auto">
                  {JSON.stringify(call.args, null, 2)}
                </pre>
              </div>

              {/* Result */}
              {call.success && call.result && (
                <div className="text-xs text-gray-600 dark:text-gray-400 ml-6 mt-2">
                  <div className="font-semibold mb-1">Result:</div>
                  <div className="bg-green-50 dark:bg-green-900/20 rounded p-2">
                    {call.result.message || 'Success'}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
```

### 7. Chat Input Component

```typescript
// components/chat/ChatInput.tsx
import React, { useState, useRef, KeyboardEvent } from 'react'
import { Send, Mic, Loader2 } from 'lucide-react'

interface ChatInputProps {
  onSend: (message: string) => void
  onVoiceInput?: () => void
  isLoading?: boolean
  disabled?: boolean
}

export function ChatInput({
  onSend,
  onVoiceInput,
  isLoading = false,
  disabled = false
}: ChatInputProps) {
  const [message, setMessage] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSend = () => {
    if (message.trim() && !isLoading && !disabled) {
      onSend(message)
      setMessage('')

      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto'
      }
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value)

    // Auto-resize textarea
    e.target.style.height = 'auto'
    e.target.style.height = `${e.target.scrollHeight}px`
  }

  return (
    <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4">
      <div className="max-w-4xl mx-auto flex items-end gap-2">
        {/* Voice Input Button */}
        {onVoiceInput && (
          <button
            onClick={onVoiceInput}
            disabled={disabled || isLoading}
            className="p-3 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title="Voice input"
          >
            <Mic size={20} className="text-gray-700 dark:text-gray-300" />
          </button>
        )}

        {/* Text Input */}
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            disabled={disabled || isLoading}
            placeholder={isLoading ? "AI is thinking..." : "Type your message... (Shift+Enter for new line)"}
            rows={1}
            className="w-full px-4 py-3 pr-12 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed resize-none max-h-32"
          />
        </div>

        {/* Send Button */}
        <button
          onClick={handleSend}
          disabled={!message.trim() || disabled || isLoading}
          className="p-3 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white transition-colors"
          title="Send message"
        >
          {isLoading ? (
            <Loader2 size={20} className="animate-spin" />
          ) : (
            <Send size={20} />
          )}
        </button>
      </div>

      {/* Helper Text */}
      <div className="max-w-4xl mx-auto mt-2 text-xs text-gray-500 dark:text-gray-400 text-center">
        Press Enter to send, Shift+Enter for new line
      </div>
    </div>
  )
}
```

### 8. Typing Indicator

```typescript
// components/chat/TypingIndicator.tsx
import React from 'react'

export function TypingIndicator() {
  return (
    <div className="flex justify-start mb-4">
      <div className="flex items-start gap-3">
        {/* AI Avatar */}
        <div className="w-8 h-8 rounded-full flex items-center justify-center bg-purple-600 text-white font-semibold">
          AI
        </div>

        {/* Typing Animation */}
        <div className="bg-gray-100 dark:bg-gray-800 rounded-2xl px-4 py-3">
          <div className="flex gap-1">
            <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0ms' }} />
            <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '150ms' }} />
            <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
        </div>
      </div>
    </div>
  )
}
```

### 9. Message List Component

```typescript
// components/chat/MessageList.tsx
import React from 'react'
import { Message } from '@/types/chat'
import { MessageBubble } from './MessageBubble'
import { TypingIndicator } from './TypingIndicator'

interface MessageListProps {
  messages: Message[]
  isTyping?: boolean
  messagesEndRef: React.RefObject<HTMLDivElement>
}

export function MessageList({ messages, isTyping, messagesEndRef }: MessageListProps) {
  if (messages.length === 0 && !isTyping) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="text-center space-y-4">
          <div className="text-6xl">💬</div>
          <h2 className="text-2xl font-semibold text-gray-700 dark:text-gray-300">
            Start a Conversation
          </h2>
          <p className="text-gray-500 dark:text-gray-400 max-w-md">
            Ask me to create tasks, search your todos, or get insights about your productivity.
          </p>
          <div className="grid grid-cols-1 gap-2 max-w-md mt-6">
            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 text-sm text-left">
              💡 Try: "Create a task to finish the report by Friday"
            </div>
            <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-3 text-sm text-left">
              💡 Try: "Show me all high priority tasks"
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 text-sm text-left">
              💡 Try: "What tasks are due this week?"
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      <div className="max-w-4xl mx-auto">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}

        {isTyping && <TypingIndicator />}

        <div ref={messagesEndRef} />
      </div>
    </div>
  )
}
```

### 10. Chat Container (Main Component)

```typescript
// components/chat/ChatContainer.tsx
'use client'

import React from 'react'
import { useChat } from '@/hooks/useChat'
import { MessageList } from './MessageList'
import { ChatInput } from './ChatInput'

interface ChatContainerProps {
  conversationId?: number
}

export function ChatContainer({ conversationId }: ChatContainerProps) {
  const { messages, isTyping, isLoading, sendMessage, messagesEndRef } = useChat(conversationId)

  return (
    <div className="flex flex-col h-screen bg-white dark:bg-gray-900">
      {/* Header */}
      <div className="border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            AI Assistant
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Your intelligent TODO management assistant
          </p>
        </div>
      </div>

      {/* Messages */}
      {isLoading ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
        </div>
      ) : (
        <MessageList
          messages={messages}
          isTyping={isTyping}
          messagesEndRef={messagesEndRef}
        />
      )}

      {/* Input */}
      <ChatInput
        onSend={sendMessage}
        isLoading={isTyping}
        disabled={isLoading}
      />
    </div>
  )
}
```

### 11. Chat Page

```typescript
// app/chat/page.tsx
import { ChatContainer } from '@/components/chat/ChatContainer'

export default function ChatPage() {
  return <ChatContainer />
}
```

---

## Styling

### Tailwind Configuration

```javascript
// tailwind.config.js
module.exports = {
  darkMode: 'class',
  theme: {
    extend: {
      typography: {
        DEFAULT: {
          css: {
            maxWidth: 'none',
            color: 'inherit',
            a: {
              color: '#3b82f6',
              '&:hover': {
                color: '#2563eb',
              },
            },
            code: {
              backgroundColor: '#f3f4f6',
              padding: '0.25rem',
              borderRadius: '0.25rem',
              fontWeight: '600',
            },
            'code::before': {
              content: '""',
            },
            'code::after': {
              content: '""',
            },
          },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
```

---

## Dependencies

```json
{
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "next": "^15.0.0",
    "@tanstack/react-query": "^5.0.0",
    "react-markdown": "^9.0.0",
    "react-syntax-highlighter": "^15.5.0",
    "lucide-react": "^0.400.0"
  },
  "devDependencies": {
    "@tailwindcss/typography": "^0.5.10",
    "typescript": "^5.0.0",
    "@types/react": "^18.3.0",
    "@types/react-syntax-highlighter": "^15.5.11"
  }
}
```

---

## Best Practices

### 1. Optimize Re-renders
```typescript
// ✅ Memoize message components
export const MessageBubble = React.memo(MessageBubbleComponent)

// ✅ Use useCallback for event handlers
const handleSend = useCallback((msg: string) => {
  sendMessage(msg)
}, [sendMessage])
```

### 2. Handle Loading States
```typescript
// ✅ Show typing indicator
{isTyping && <TypingIndicator />}

// ✅ Disable input while loading
<ChatInput disabled={isTyping || isLoading} />
```

### 3. Auto-scroll to Bottom
```typescript
// ✅ Smooth scroll on new messages
useEffect(() => {
  messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
}, [messages])
```

### 4. Error Handling
```typescript
// ✅ Show error messages in chat
if (error) {
  const errorMsg: Message = {
    role: 'assistant',
    content: 'Sorry, something went wrong. Please try again.',
    timestamp: new Date()
  }
  setMessages(prev => [...prev, errorMsg])
}
```

### 5. Accessibility
```typescript
// ✅ Add ARIA labels
<button aria-label="Send message" title="Send message">
  <Send />
</button>

// ✅ Keyboard navigation
<textarea
  onKeyDown={(e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }}
/>
```

---

## Testing

```typescript
// __tests__/chat/MessageBubble.test.tsx
import { render, screen } from '@testing-library/react'
import { MessageBubble } from '@/components/chat/MessageBubble'

describe('MessageBubble', () => {
  it('renders user message correctly', () => {
    const message = {
      id: '1',
      role: 'user' as const,
      content: 'Hello AI',
      timestamp: new Date()
    }

    render(<MessageBubble message={message} />)

    expect(screen.getByText('Hello AI')).toBeInTheDocument()
    expect(screen.getByText('U')).toBeInTheDocument() // User avatar
  })

  it('renders assistant message with markdown', () => {
    const message = {
      id: '2',
      role: 'assistant' as const,
      content: '**Bold text** and *italic*',
      timestamp: new Date()
    }

    render(<MessageBubble message={message} />)

    expect(screen.getByText(/Bold text/)).toBeInTheDocument()
  })
})
```

---

## Performance Optimization

### 1. Virtual Scrolling for Long Chats
```typescript
import { useVirtualizer } from '@tanstack/react-virtual'

// For conversations with 100+ messages
const virtualizer = useVirtualizer({
  count: messages.length,
  getScrollElement: () => scrollRef.current,
  estimateSize: () => 100,
})
```

### 2. Lazy Load Conversations
```typescript
// Load conversations on demand
const { data, fetchNextPage } = useInfiniteQuery({
  queryKey: ['conversations'],
  queryFn: ({ pageParam = 0 }) =>
    ChatAPI.getConversations(pageParam),
  getNextPageParam: (lastPage) => lastPage.nextCursor,
})
```

### 3. Debounce Typing Indicator
```typescript
// Show "AI is typing" after slight delay
const [showTyping, setShowTyping] = useState(false)

useEffect(() => {
  const timer = setTimeout(() => setShowTyping(isTyping), 300)
  return () => clearTimeout(timer)
}, [isTyping])
```

---

## Mobile Responsive Design

```typescript
// Responsive layout
<div className="
  h-screen
  flex flex-col
  md:flex-row
">
  {/* Sidebar - hidden on mobile */}
  <aside className="
    hidden md:block
    w-64 border-r
  ">
    <ConversationList />
  </aside>

  {/* Chat - full width on mobile */}
  <main className="flex-1">
    <ChatContainer />
  </main>
</div>
```

---

**Last Updated:** 2026-01-12
**Skill Version:** 1.0.0
**Recommended For:** Phase 3 AI Chatbot - Frontend Chat UI
