# Skill: AI Voice Input

## Description
Implement speech-to-text voice input for hands-free TODO management using Web Speech API and modern browser capabilities. Enable users to create and manage tasks through voice commands.

## When to Use
- Adding voice input to chat interface
- Implementing speech-to-text functionality
- Creating hands-free task management
- Building voice-activated features
- Enhancing accessibility for users

## Prerequisites
- Modern browser with Web Speech API support
- React/Next.js application
- Microphone permissions
- HTTPS (required for Web Speech API)
- Audio recording capabilities

---

## Core Concepts

### Web Speech API
- **SpeechRecognition**: Converts speech to text in real-time
- **Browser Support**: Chrome, Edge, Safari (with webkit prefix)
- **Languages**: Multiple language support (en-US, es-ES, etc.)
- **Continuous Mode**: Can listen continuously or one-shot
- **Interim Results**: Get results while user is still speaking

### Voice Command Patterns
1. **Direct Commands**: "Create task to finish report"
2. **Natural Language**: "Remind me to call John tomorrow"
3. **Queries**: "What are my high priority tasks?"
4. **Actions**: "Mark task 5 as done"

---

## Implementation

### 1. Voice Input Hook

```typescript
// hooks/useVoiceInput.ts
import { useState, useEffect, useCallback, useRef } from 'react'

interface VoiceInputOptions {
  lang?: string
  continuous?: boolean
  interimResults?: boolean
  onResult?: (transcript: string) => void
  onError?: (error: string) => void
}

interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList
  resultIndex: number
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string
  message: string
}

// Extend Window interface for TypeScript
declare global {
  interface Window {
    SpeechRecognition: any
    webkitSpeechRecognition: any
  }
}

export function useVoiceInput(options: VoiceInputOptions = {}) {
  const {
    lang = 'en-US',
    continuous = false,
    interimResults = true,
    onResult,
    onError
  } = options

  const [isListening, setIsListening] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [interimTranscript, setInterimTranscript] = useState('')
  const [isSupported, setIsSupported] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const recognitionRef = useRef<any>(null)

  // Check browser support
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition

    if (SpeechRecognition) {
      setIsSupported(true)

      // Initialize speech recognition
      const recognition = new SpeechRecognition()
      recognition.continuous = continuous
      recognition.interimResults = interimResults
      recognition.lang = lang
      recognition.maxAlternatives = 1

      // Event handlers
      recognition.onstart = () => {
        setIsListening(true)
        setError(null)
        console.log('Voice recognition started')
      }

      recognition.onend = () => {
        setIsListening(false)
        console.log('Voice recognition ended')
      }

      recognition.onresult = (event: SpeechRecognitionEvent) => {
        let interimText = ''
        let finalText = ''

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const result = event.results[i]
          const text = result[0].transcript

          if (result.isFinal) {
            finalText += text
          } else {
            interimText += text
          }
        }

        if (finalText) {
          setTranscript(prev => prev + ' ' + finalText)
          setInterimTranscript('')

          if (onResult) {
            onResult(finalText.trim())
          }

          // Auto-stop if not continuous
          if (!continuous) {
            recognition.stop()
          }
        } else {
          setInterimTranscript(interimText)
        }
      }

      recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
        console.error('Speech recognition error:', event.error)

        let errorMessage = 'Voice input error'

        switch (event.error) {
          case 'no-speech':
            errorMessage = 'No speech detected. Please try again.'
            break
          case 'audio-capture':
            errorMessage = 'No microphone detected. Please check your microphone.'
            break
          case 'not-allowed':
            errorMessage = 'Microphone permission denied. Please allow microphone access.'
            break
          case 'network':
            errorMessage = 'Network error. Please check your internet connection.'
            break
          default:
            errorMessage = `Voice input error: ${event.error}`
        }

        setError(errorMessage)
        setIsListening(false)

        if (onError) {
          onError(errorMessage)
        }
      }

      recognitionRef.current = recognition
    } else {
      setIsSupported(false)
      console.warn('Speech Recognition API not supported in this browser')
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop()
      }
    }
  }, [lang, continuous, interimResults, onResult, onError])

  // Start listening
  const startListening = useCallback(async () => {
    if (!isSupported) {
      const errorMsg = 'Voice input is not supported in this browser'
      setError(errorMsg)
      if (onError) onError(errorMsg)
      return
    }

    try {
      // Request microphone permission
      await navigator.mediaDevices.getUserMedia({ audio: true })

      if (recognitionRef.current && !isListening) {
        setTranscript('')
        setInterimTranscript('')
        setError(null)
        recognitionRef.current.start()
      }
    } catch (err: any) {
      const errorMsg = err.name === 'NotAllowedError'
        ? 'Microphone permission denied'
        : 'Failed to access microphone'

      setError(errorMsg)
      if (onError) onError(errorMsg)
    }
  }, [isSupported, isListening, onError])

  // Stop listening
  const stopListening = useCallback(() => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop()
    }
  }, [isListening])

  // Reset transcript
  const resetTranscript = useCallback(() => {
    setTranscript('')
    setInterimTranscript('')
    setError(null)
  }, [])

  return {
    isListening,
    transcript,
    interimTranscript,
    isSupported,
    error,
    startListening,
    stopListening,
    resetTranscript
  }
}
```

### 2. Voice Button Component

```typescript
// components/chat/VoiceButton.tsx
'use client'

import React, { useState, useEffect } from 'react'
import { Mic, MicOff, Loader2 } from 'lucide-react'
import { useVoiceInput } from '@/hooks/useVoiceInput'

interface VoiceButtonProps {
  onTranscript: (text: string) => void
  disabled?: boolean
}

export function VoiceButton({ onTranscript, disabled = false }: VoiceButtonProps) {
  const [showTranscript, setShowTranscript] = useState(false)

  const {
    isListening,
    transcript,
    interimTranscript,
    isSupported,
    error,
    startListening,
    stopListening,
    resetTranscript
  } = useVoiceInput({
    continuous: false,
    interimResults: true,
    onResult: (text) => {
      // Send transcript to parent
      onTranscript(text)
      setShowTranscript(false)
      resetTranscript()
    },
    onError: (err) => {
      console.error('Voice input error:', err)
      setShowTranscript(false)
    }
  })

  const handleClick = () => {
    if (isListening) {
      stopListening()
      setShowTranscript(false)
    } else {
      startListening()
      setShowTranscript(true)
    }
  }

  useEffect(() => {
    if (!isListening && showTranscript) {
      setShowTranscript(false)
    }
  }, [isListening, showTranscript])

  if (!isSupported) {
    return null // Don't show button if not supported
  }

  return (
    <div className="relative">
      <button
        onClick={handleClick}
        disabled={disabled}
        className={`
          p-3 rounded-lg transition-all duration-200
          ${isListening
            ? 'bg-red-600 hover:bg-red-700 animate-pulse'
            : 'bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600'
          }
          ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
        `}
        title={isListening ? 'Stop listening' : 'Start voice input'}
      >
        {isListening ? (
          <MicOff size={20} className="text-white" />
        ) : (
          <Mic size={20} className="text-gray-700 dark:text-gray-300" />
        )}
      </button>

      {/* Listening indicator */}
      {isListening && (
        <div className="absolute -bottom-12 left-1/2 transform -translate-x-1/2 whitespace-nowrap">
          <div className="bg-red-600 text-white px-3 py-1 rounded-full text-xs font-medium flex items-center gap-2">
            <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
            Listening...
          </div>
        </div>
      )}

      {/* Transcript overlay */}
      {showTranscript && (transcript || interimTranscript) && (
        <div className="absolute bottom-16 left-1/2 transform -translate-x-1/2 w-64 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg p-3">
          <div className="text-sm">
            <div className="font-semibold text-gray-900 dark:text-gray-100 mb-1">
              Voice Input
            </div>
            <div className="text-gray-700 dark:text-gray-300">
              {transcript}
              <span className="text-gray-400 dark:text-gray-500">
                {interimTranscript}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Error message */}
      {error && (
        <div className="absolute bottom-16 left-1/2 transform -translate-x-1/2 w-64 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg shadow-lg p-3">
          <div className="text-sm text-red-700 dark:text-red-300">
            {error}
          </div>
        </div>
      )}
    </div>
  )
}
```

### 3. Integrated Chat Input with Voice

```typescript
// components/chat/ChatInputWithVoice.tsx
'use client'

import React, { useState, useRef, KeyboardEvent } from 'react'
import { Send, Loader2 } from 'lucide-react'
import { VoiceButton } from './VoiceButton'

interface ChatInputWithVoiceProps {
  onSend: (message: string) => void
  isLoading?: boolean
  disabled?: boolean
}

export function ChatInputWithVoice({
  onSend,
  isLoading = false,
  disabled = false
}: ChatInputWithVoiceProps) {
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

  const handleVoiceTranscript = (text: string) => {
    // Auto-send voice transcript
    if (text.trim()) {
      onSend(text.trim())
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
        <VoiceButton
          onTranscript={handleVoiceTranscript}
          disabled={disabled || isLoading}
        />

        {/* Text Input */}
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            disabled={disabled || isLoading}
            placeholder={isLoading ? "AI is thinking..." : "Type or speak your message..."}
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
        Click microphone to speak, or type your message
      </div>
    </div>
  )
}
```

### 4. Voice Command Parser (Backend)

```python
# backend/agents/voice_commands.py
import re
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

class VoiceCommandParser:
    """
    Parse natural language voice commands into structured actions.
    """

    # Command patterns
    CREATE_PATTERNS = [
        r"create (?:a )?task (?:to )?(.+)",
        r"add (?:a )?task (?:to )?(.+)",
        r"remind me to (.+)",
        r"i need to (.+)",
    ]

    PRIORITY_PATTERNS = {
        "high": r"\b(urgent|important|critical|asap|high priority)\b",
        "medium": r"\b(medium priority|normal)\b",
        "low": r"\b(low priority|not urgent|when (?:i|you) (?:can|have time))\b",
    }

    TIME_PATTERNS = {
        "today": r"\btoday\b",
        "tomorrow": r"\btomorrow\b",
        "next_week": r"\bnext week\b",
        "this_week": r"\bthis week\b",
    }

    @classmethod
    def parse(cls, text: str) -> Dict[str, Any]:
        """
        Parse voice command text into structured command.

        Args:
            text: Voice transcript

        Returns:
            Dict with command type and parameters
        """
        text_lower = text.lower().strip()

        # Check for create task commands
        for pattern in cls.CREATE_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                task_text = match.group(1)
                return cls._parse_create_task(task_text)

        # Check for query commands
        if cls._is_query(text_lower):
            return cls._parse_query(text_lower)

        # Check for update commands
        if cls._is_update(text_lower):
            return cls._parse_update(text_lower)

        # Default: treat as general query
        return {
            "type": "query",
            "query": text
        }

    @classmethod
    def _parse_create_task(cls, task_text: str) -> Dict[str, Any]:
        """Parse create task command"""
        # Extract priority
        priority = "medium"
        for pri, pattern in cls.PRIORITY_PATTERNS.items():
            if re.search(pattern, task_text):
                priority = pri
                # Remove priority keywords from task text
                task_text = re.sub(pattern, "", task_text).strip()
                break

        # Extract due date
        due_date = None
        for time_key, pattern in cls.TIME_PATTERNS.items():
            if re.search(pattern, task_text):
                due_date = cls._calculate_due_date(time_key)
                # Remove time keywords from task text
                task_text = re.sub(pattern, "", task_text).strip()
                break

        # Clean up task text
        task_text = re.sub(r'\s+', ' ', task_text).strip()

        return {
            "type": "create_task",
            "title": task_text,
            "priority": priority,
            "due_date": due_date.isoformat() if due_date else None
        }

    @classmethod
    def _is_query(cls, text: str) -> bool:
        """Check if text is a query command"""
        query_keywords = [
            "show", "list", "what", "which", "how many",
            "get", "find", "search", "display"
        ]
        return any(keyword in text for keyword in query_keywords)

    @classmethod
    def _parse_query(cls, text: str) -> Dict[str, Any]:
        """Parse query command"""
        filters = {}

        # Extract priority filter
        if "high priority" in text:
            filters["priority"] = "high"
        elif "low priority" in text:
            filters["priority"] = "low"

        # Extract status filter
        if "done" in text or "completed" in text:
            filters["status"] = "done"
        elif "in progress" in text:
            filters["status"] = "in_progress"

        return {
            "type": "get_tasks",
            "filters": filters
        }

    @classmethod
    def _is_update(cls, text: str) -> bool:
        """Check if text is an update command"""
        update_keywords = [
            "mark", "complete", "finish", "update",
            "change", "set", "move"
        ]
        return any(keyword in text for keyword in update_keywords)

    @classmethod
    def _parse_update(cls, text: str) -> Dict[str, Any]:
        """Parse update command"""
        # Extract task identifier (number or title)
        task_id_match = re.search(r"task (\d+)", text)
        task_id = int(task_id_match.group(1)) if task_id_match else None

        # Extract new status
        status = None
        if "done" in text or "complete" in text:
            status = "done"
        elif "in progress" in text:
            status = "in_progress"

        return {
            "type": "update_task",
            "task_id": task_id,
            "updates": {
                "status": status
            } if status else {}
        }

    @classmethod
    def _calculate_due_date(cls, time_key: str) -> Optional[datetime]:
        """Calculate due date from time keyword"""
        now = datetime.now()

        if time_key == "today":
            return now
        elif time_key == "tomorrow":
            return now + timedelta(days=1)
        elif time_key == "next_week":
            return now + timedelta(weeks=1)
        elif time_key == "this_week":
            # Next Friday
            days_until_friday = (4 - now.weekday()) % 7
            if days_until_friday == 0:
                days_until_friday = 7
            return now + timedelta(days=days_until_friday)

        return None
```

### 5. Voice Command API Endpoint

```python
# backend/routes/voice.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.auth import get_current_user
from agents.voice_commands import VoiceCommandParser
from agents.openai_agent import OpenAIAgent
from agents.tools import get_mcp_tools

router = APIRouter(prefix="/api/voice", tags=["voice"])

class VoiceCommandRequest(BaseModel):
    transcript: str

class VoiceCommandResponse(BaseModel):
    understood: bool
    command_type: str
    response: str
    action_taken: dict = {}

@router.post("/command", response_model=VoiceCommandResponse)
async def process_voice_command(
    request: VoiceCommandRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Process voice command transcript.

    Parses the voice command and executes appropriate action.
    """
    # Parse command
    parsed = VoiceCommandParser.parse(request.transcript)

    # If it's a simple command, execute directly
    if parsed["type"] == "create_task":
        from mcp_server.tools.tasks import create_task

        result = await create_task(
            user_id=current_user.id,
            title=parsed["title"],
            priority=parsed.get("priority", "medium"),
            due_date=parsed.get("due_date")
        )

        return VoiceCommandResponse(
            understood=True,
            command_type="create_task",
            response=f"Created task: {parsed['title']}",
            action_taken=result
        )

    # For complex commands, use AI agent
    else:
        agent = OpenAIAgent()
        tools = get_mcp_tools()
        await agent.register_tools(tools)

        messages = [
            {"role": "user", "content": request.transcript}
        ]

        response, tool_calls = await agent.run(
            messages=messages,
            user_id=current_user.id
        )

        return VoiceCommandResponse(
            understood=True,
            command_type=parsed["type"],
            response=response,
            action_taken={"tool_calls": tool_calls}
        )
```

---

## Browser Compatibility

### Supported Browsers
- ✅ Chrome 25+ (Windows, Mac, Android)
- ✅ Edge 79+
- ✅ Safari 14.1+ (iOS, macOS)
- ❌ Firefox (Limited support)
- ❌ Opera (Limited support)

### Feature Detection

```typescript
// Check if browser supports speech recognition
const isSupported = !!(window.SpeechRecognition || window.webkitSpeechRecognition)

if (!isSupported) {
  console.warn('Speech recognition not supported')
  // Hide voice button or show fallback
}
```

---

## Security & Privacy

### HTTPS Required
```typescript
// Voice input only works on HTTPS
if (location.protocol !== 'https:' && location.hostname !== 'localhost') {
  console.error('Voice input requires HTTPS')
}
```

### Microphone Permissions
```typescript
// Request permission explicitly
try {
  await navigator.mediaDevices.getUserMedia({ audio: true })
  console.log('Microphone permission granted')
} catch (err) {
  console.error('Microphone permission denied')
}
```

### Data Privacy
- Voice data processed by browser's speech recognition service
- No audio sent to your server (only transcripts)
- User can revoke microphone permission anytime

---

## Best Practices

### 1. Show Clear Visual Feedback
```typescript
// ✅ Show listening state
{isListening && (
  <div className="animate-pulse text-red-600">
    🎤 Listening...
  </div>
)}
```

### 2. Handle Errors Gracefully
```typescript
// ✅ User-friendly error messages
if (error === 'no-speech') {
  showMessage("I didn't hear anything. Please try again.")
}
```

### 3. Auto-Send Transcripts
```typescript
// ✅ Send immediately after speech ends
onResult: (text) => {
  sendMessage(text)
}
```

### 4. Provide Text Alternative
```typescript
// ✅ Always allow typing as fallback
<textarea placeholder="Type or speak..." />
<VoiceButton />
```

### 5. Multi-Language Support
```typescript
// ✅ Support user's language
const userLang = navigator.language || 'en-US'
useVoiceInput({ lang: userLang })
```

---

## Testing

```typescript
// __tests__/voice/VoiceButton.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { VoiceButton } from '@/components/chat/VoiceButton'

// Mock Web Speech API
beforeEach(() => {
  global.SpeechRecognition = jest.fn(() => ({
    start: jest.fn(),
    stop: jest.fn(),
    addEventListener: jest.fn(),
  }))
})

describe('VoiceButton', () => {
  it('renders when supported', () => {
    render(<VoiceButton onTranscript={jest.fn()} />)
    expect(screen.getByTitle(/voice input/i)).toBeInTheDocument()
  })

  it('starts listening on click', () => {
    const onTranscript = jest.fn()
    render(<VoiceButton onTranscript={onTranscript} />)

    const button = screen.getByRole('button')
    fireEvent.click(button)

    // Should show listening indicator
    expect(screen.getByText(/listening/i)).toBeInTheDocument()
  })
})
```

---

## Troubleshooting

### Issue: "Microphone permission denied"
**Solution:** User must manually allow microphone access in browser settings

### Issue: "No speech detected"
**Solution:** Check microphone is working, increase volume, reduce background noise

### Issue: "Network error"
**Solution:** Speech recognition requires internet connection (browser API limitation)

### Issue: "Works on desktop but not mobile"
**Solution:** Ensure HTTPS is enabled, check mobile browser compatibility

---

**Last Updated:** 2026-01-12
**Skill Version:** 1.0.0
**Recommended For:** Phase 3 AI Chatbot - Voice Input Feature
