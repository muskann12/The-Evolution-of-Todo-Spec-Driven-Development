# Skill: Chatbot Conversation Management (Stateless)

## Description
Implement stateless conversation management with database persistence for AI chatbots. Store all conversation state in the database, enabling server restarts without data loss and truly scalable, stateless architecture.

## When to Use
- Building stateless chatbot backends
- Implementing conversation persistence
- Managing multi-turn dialogs without sessions
- Scaling chatbots horizontally
- Ensuring conversation continuity after restarts
- Building cloud-native AI applications

## Prerequisites
- SQLModel or SQLAlchemy for database ORM
- PostgreSQL or similar relational database
- Understanding of stateless architecture
- Async Python (asyncio, FastAPI)
- Basic understanding of REST APIs

---

## Core Concepts

### Stateless Architecture Principles

**Stateless** means the server holds NO conversation state in memory:
- ❌ No server-side sessions
- ❌ No in-memory conversation storage
- ❌ No global variables tracking conversations
- ✅ All state stored in database
- ✅ Every request is independent
- ✅ Server can restart anytime without data loss

### Why Stateless?

1. **Scalability**: Add/remove servers without coordination
2. **Reliability**: Server crashes don't lose conversations
3. **Cloud-Native**: Works with containers, serverless, etc.
4. **Simplicity**: No complex session management

### Request Flow

```
User Request
    ↓
1. Authenticate user (get user_id)
    ↓
2. Get or create conversation
    ↓
3. Fetch last N messages from database
    ↓
4. Add user message to database
    ↓
5. Build message array for AI
    ↓
6. Call AI agent
    ↓
7. Store AI response in database
    ↓
8. Return response
```

**Key Point**: Every request starts fresh by fetching from database!

---

## Implementation

### 1. Database Models (SQLModel)

```python
# models/conversation.py
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from typing import Optional, List

class Conversation(SQLModel, table=True):
    """
    Conversation thread between user and AI.

    Stateless design: No conversation state in memory.
    All state stored here in database.
    """
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)  # CRITICAL: Always filter by this
    title: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")

    class Config:
        schema_extra = {
            "example": {
                "user_id": 1,
                "title": "Task Management Chat"
            }
        }


class Message(SQLModel, table=True):
    """
    Individual message in a conversation.

    Stores complete message history in database.
    Server never keeps messages in memory.
    """
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    role: str = Field(max_length=20)  # "user", "assistant", "system"
    content: str = Field(sa_column_kwargs={"type_": "TEXT"})
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: Optional[Conversation] = Relationship(back_populates="messages")

    class Config:
        schema_extra = {
            "example": {
                "conversation_id": 1,
                "role": "user",
                "content": "Create a task to finish the report"
            }
        }


# Create indexes for fast queries
# Add to migration file:
# CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at DESC);
# CREATE INDEX idx_conversations_user_updated ON conversations(user_id, updated_at DESC);
```

### 2. Conversation Service (Stateless)

```python
# services/conversation_service.py
from typing import List, Dict, Any, Optional
from sqlmodel import Session, select, and_
from datetime import datetime
from models.conversation import Conversation, Message

class ConversationService:
    """
    Stateless conversation management.

    IMPORTANT: This class is stateless!
    - No instance variables storing conversations
    - All methods fetch fresh data from database
    - Can be instantiated per-request
    """

    def __init__(self, db: Session):
        """
        Initialize with database session.

        Args:
            db: Database session (per-request)
        """
        self.db = db

    def get_or_create_conversation(
        self,
        user_id: int,
        conversation_id: Optional[int] = None,
        title: Optional[str] = None
    ) -> Conversation:
        """
        Get existing conversation or create new one.

        Stateless: Fetches from database every time.

        Args:
            user_id: User ID (for security filtering)
            conversation_id: Existing conversation ID (optional)
            title: Title for new conversation (optional)

        Returns:
            Conversation object
        """
        if conversation_id:
            # Fetch existing conversation (with user_id filter!)
            statement = select(Conversation).where(
                and_(
                    Conversation.id == conversation_id,
                    Conversation.user_id == user_id  # CRITICAL: Security check
                )
            )
            conversation = self.db.exec(statement).first()

            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found or access denied")

            return conversation

        else:
            # Create new conversation
            conversation = Conversation(
                user_id=user_id,
                title=title or f"Chat {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)

            return conversation

    def add_user_message(
        self,
        conversation_id: int,
        user_id: int,
        content: str
    ) -> Message:
        """
        Store user message in database.

        Args:
            conversation_id: Conversation ID
            user_id: User ID (for security)
            content: Message content

        Returns:
            Created message
        """
        # Verify user owns this conversation
        conversation = self.get_or_create_conversation(user_id, conversation_id)

        # Create message
        message = Message(
            conversation_id=conversation.id,
            role="user",
            content=content,
            created_at=datetime.utcnow()
        )

        self.db.add(message)

        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(message)

        return message

    def add_assistant_message(
        self,
        conversation_id: int,
        user_id: int,
        content: str
    ) -> Message:
        """
        Store assistant message in database.

        Args:
            conversation_id: Conversation ID
            user_id: User ID (for security)
            content: AI response content

        Returns:
            Created message
        """
        # Verify user owns this conversation
        conversation = self.get_or_create_conversation(user_id, conversation_id)

        # Create message
        message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=content,
            created_at=datetime.utcnow()
        )

        self.db.add(message)

        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(message)

        return message

    def get_conversation_history(
        self,
        conversation_id: int,
        user_id: int,
        limit: int = 20
    ) -> List[Message]:
        """
        Fetch conversation history from database.

        Stateless: Always fetches fresh from database.
        Limits messages to prevent huge context windows.

        Args:
            conversation_id: Conversation ID
            user_id: User ID (for security)
            limit: Maximum messages to fetch (default: 20)

        Returns:
            List of messages (oldest first)
        """
        # Verify user owns this conversation
        self.get_or_create_conversation(user_id, conversation_id)

        # Fetch last N messages
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )

        messages = self.db.exec(statement).all()

        # Reverse to get oldest-first (chronological order)
        return list(reversed(messages))

    def build_message_array(
        self,
        conversation_id: int,
        user_id: int,
        system_prompt: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, str]]:
        """
        Build message array for AI agent.

        Converts database messages to OpenAI format.
        Includes optional system prompt.

        Args:
            conversation_id: Conversation ID
            user_id: User ID (for security)
            system_prompt: Optional system prompt to prepend
            limit: Maximum messages to include

        Returns:
            List of message dicts in OpenAI format
        """
        # Get conversation history
        history = self.get_conversation_history(
            conversation_id,
            user_id,
            limit
        )

        # Build message array
        messages = []

        # Add system prompt if provided
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })

        # Add conversation history
        for msg in history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

        return messages

    def list_user_conversations(
        self,
        user_id: int,
        limit: int = 50
    ) -> List[Conversation]:
        """
        List all conversations for a user.

        Args:
            user_id: User ID
            limit: Maximum conversations to return

        Returns:
            List of conversations (most recent first)
        """
        statement = (
            select(Conversation)
            .where(
                and_(
                    Conversation.user_id == user_id,
                    Conversation.is_active == True
                )
            )
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
        )

        return list(self.db.exec(statement).all())

    def delete_conversation(
        self,
        conversation_id: int,
        user_id: int
    ) -> bool:
        """
        Delete a conversation (soft delete).

        Args:
            conversation_id: Conversation ID
            user_id: User ID (for security)

        Returns:
            True if deleted, False if not found
        """
        # Verify user owns this conversation
        try:
            conversation = self.get_or_create_conversation(user_id, conversation_id)
        except ValueError:
            return False

        # Soft delete
        conversation.is_active = False
        self.db.commit()

        return True
```

### 3. FastAPI Endpoint (Stateless)

```python
# routes/chat.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from sqlmodel import Session
from app.database import get_db
from app.auth import get_current_user
from services.conversation_service import ConversationService
from agents.openai_agent import OpenAIAgent

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    """Request to send a message."""
    message: str
    conversation_id: Optional[int] = None


class ChatResponse(BaseModel):
    """Response with AI message."""
    response: str
    conversation_id: int


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Send a message to AI chatbot.

    STATELESS DESIGN:
    1. Every request is independent
    2. Fetch conversation history from database
    3. Process message
    4. Store results in database
    5. Return response

    Server can restart between requests without losing data!
    """
    # Initialize stateless service (per-request)
    conversation_service = ConversationService(db)

    # Step 1: Get or create conversation
    conversation = conversation_service.get_or_create_conversation(
        user_id=current_user.id,
        conversation_id=request.conversation_id
    )

    # Step 2: Store user message in database
    conversation_service.add_user_message(
        conversation_id=conversation.id,
        user_id=current_user.id,
        content=request.message
    )

    # Step 3: Build message array from database (last 20 messages)
    messages = conversation_service.build_message_array(
        conversation_id=conversation.id,
        user_id=current_user.id,
        system_prompt="You are a helpful TODO management assistant.",
        limit=20  # Limit context window
    )

    # Step 4: Call AI agent (stateless)
    agent = OpenAIAgent()
    ai_response = await agent.generate_response(messages)

    # Step 5: Store assistant message in database
    conversation_service.add_assistant_message(
        conversation_id=conversation.id,
        user_id=current_user.id,
        content=ai_response
    )

    # Step 6: Return response
    return ChatResponse(
        response=ai_response,
        conversation_id=conversation.id
    )


@router.get("/conversations")
async def list_conversations(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    List all conversations for current user.

    Stateless: Fetches fresh from database.
    """
    conversation_service = ConversationService(db)

    conversations = conversation_service.list_user_conversations(
        user_id=current_user.id,
        limit=50
    )

    return {
        "conversations": [
            {
                "id": conv.id,
                "title": conv.title,
                "created_at": conv.created_at,
                "updated_at": conv.updated_at
            }
            for conv in conversations
        ]
    }


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get messages for a conversation.

    Stateless: Fetches fresh from database.
    """
    conversation_service = ConversationService(db)

    messages = conversation_service.get_conversation_history(
        conversation_id=conversation_id,
        user_id=current_user.id,
        limit=100  # Show more for history view
    )

    return {
        "messages": [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at
            }
            for msg in messages
        ]
    }


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Delete a conversation.

    Stateless: Operates directly on database.
    """
    conversation_service = ConversationService(db)

    deleted = conversation_service.delete_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id
    )

    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {"message": "Conversation deleted"}
```

### 4. Database Migration

```python
# alembic/versions/xxx_add_conversations.py
"""Add conversations and messages tables

Revision ID: xxx
Create Date: 2026-01-12
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE')
    )

    # Create indexes for fast queries
    op.create_index(
        'idx_conversations_user_updated',
        'conversations',
        ['user_id', 'updated_at'],
        postgresql_using='btree'
    )

    op.create_index(
        'idx_messages_conversation_created',
        'messages',
        ['conversation_id', 'created_at'],
        postgresql_using='btree'
    )

def downgrade():
    op.drop_index('idx_messages_conversation_created')
    op.drop_index('idx_conversations_user_updated')
    op.drop_table('messages')
    op.drop_table('conversations')
```

---

## Stateless Architecture Checklist

### ✅ DO (Stateless)

```python
# ✅ CORRECT: Fetch from database every request
def send_message(request, db, user):
    # Fresh from database
    conversation = db.get(Conversation, request.conversation_id)
    messages = db.query(Message).filter(...).all()
    # Process...
    return response

# ✅ CORRECT: Per-request service instance
service = ConversationService(db)  # New instance each request

# ✅ CORRECT: Store everything in database
message = Message(content=text)
db.add(message)
db.commit()
```

### ❌ DON'T (Stateful)

```python
# ❌ WRONG: Storing conversations in memory
conversations = {}  # Global variable - BAD!

def send_message(request):
    conv = conversations.get(request.conversation_id)  # Memory lookup - BAD!
    # If server restarts, conversations dict is GONE!

# ❌ WRONG: Server-side session
session['conversation_id'] = 123  # Session state - BAD!

# ❌ WRONG: Instance variables
class ChatService:
    def __init__(self):
        self.conversations = []  # Instance state - BAD!
```

---

## Context Window Management

### Why Limit Messages?

```python
# Problem: Unlimited history
messages = db.query(Message).filter(
    Message.conversation_id == conv_id
).all()  # Could be 1000+ messages!

# AI models have token limits
# GPT-4o: 128K tokens ≈ 96K words ≈ 1000 messages
# Sending all messages = expensive + slow

# Solution: Limit to recent messages
messages = db.query(Message).filter(
    Message.conversation_id == conv_id
).order_by(Message.created_at.desc()).limit(20).all()  # Last 20 only
```

### Recommended Limits

| Use Case | Message Limit | Why |
|----------|---------------|-----|
| Normal chat | 20 messages | Good balance of context vs cost |
| Long conversation | 30 messages | More context, higher cost |
| Quick queries | 10 messages | Fast, cheap |
| History view | 100+ messages | For display, not AI input |

---

## Security: User Isolation

### Always Filter by user_id

```python
# ✅ CORRECT: Always include user_id filter
conversation = db.query(Conversation).filter(
    Conversation.id == conv_id,
    Conversation.user_id == user.id  # CRITICAL!
).first()

# ❌ WRONG: Missing user_id check
conversation = db.query(Conversation).filter(
    Conversation.id == conv_id
).first()  # Any user can access any conversation!
```

### Why This Matters

```
User A: "Show me conversation 123"
Without user_id check: Shows User B's conversation! 🚨
With user_id check: Returns None (access denied) ✅
```

---

## Testing Stateless Architecture

### Test 1: Server Restart

```python
@pytest.mark.asyncio
async def test_conversation_persists_after_restart(db, user):
    """Test that conversations survive server restart."""

    # Create conversation
    service = ConversationService(db)
    conv = service.get_or_create_conversation(user.id)
    service.add_user_message(conv.id, user.id, "Hello")

    # Simulate server restart: create NEW service instance
    # (In real scenario, db session would also be new)
    new_service = ConversationService(db)

    # Fetch conversation (should still exist)
    messages = new_service.get_conversation_history(conv.id, user.id)

    assert len(messages) == 1
    assert messages[0].content == "Hello"
```

### Test 2: User Isolation

```python
@pytest.mark.asyncio
async def test_user_cannot_access_other_conversations(db, user1, user2):
    """Test that users can only access their own conversations."""

    service = ConversationService(db)

    # User 1 creates conversation
    conv1 = service.get_or_create_conversation(user1.id)
    service.add_user_message(conv1.id, user1.id, "User 1 message")

    # User 2 tries to access User 1's conversation
    with pytest.raises(ValueError, match="not found or access denied"):
        service.get_conversation_history(conv1.id, user2.id)
```

### Test 3: Context Window Limit

```python
@pytest.mark.asyncio
async def test_context_window_limit(db, user):
    """Test that message history is limited."""

    service = ConversationService(db)
    conv = service.get_or_create_conversation(user.id)

    # Add 50 messages
    for i in range(50):
        service.add_user_message(conv.id, user.id, f"Message {i}")

    # Fetch with limit=20
    messages = service.get_conversation_history(conv.id, user.id, limit=20)

    # Should only get last 20
    assert len(messages) == 20

    # Should be most recent (messages 30-49)
    assert "Message 30" in messages[0].content
    assert "Message 49" in messages[-1].content
```

---

## Performance Optimization

### Database Indexes

```sql
-- Critical indexes for fast queries

-- Index for fetching user's conversations
CREATE INDEX idx_conversations_user_updated
ON conversations(user_id, updated_at DESC);

-- Index for fetching conversation messages
CREATE INDEX idx_messages_conversation_created
ON messages(conversation_id, created_at DESC);

-- These indexes make queries O(log n) instead of O(n)
```

### Query Performance

```python
# ✅ EFFICIENT: Single query with limit
messages = db.query(Message).filter(
    Message.conversation_id == conv_id
).order_by(Message.created_at.desc()).limit(20).all()

# ❌ INEFFICIENT: Fetch all then slice in Python
all_messages = db.query(Message).filter(
    Message.conversation_id == conv_id
).all()
messages = all_messages[-20:]  # Slicing in Python - SLOW!
```

---

## Common Mistakes

### Mistake 1: Storing State in Memory

```python
# ❌ WRONG
class ChatBot:
    def __init__(self):
        self.conversations = {}  # Memory storage

    def send_message(self, user_id, message):
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        self.conversations[user_id].append(message)

# Problem: Lost on restart!
```

**Fix**: Always use database for state

```python
# ✅ CORRECT
def send_message(db, user_id, message):
    # Store in database
    msg = Message(user_id=user_id, content=message)
    db.add(msg)
    db.commit()
```

### Mistake 2: Missing user_id Filter

```python
# ❌ WRONG: Security vulnerability
def get_conversation(db, conversation_id):
    return db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

# ✅ CORRECT: Always filter by user
def get_conversation(db, conversation_id, user_id):
    return db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    ).first()
```

### Mistake 3: Unlimited Context Window

```python
# ❌ WRONG: Can fetch 1000+ messages
messages = db.query(Message).all()

# ✅ CORRECT: Limit to recent messages
messages = db.query(Message).order_by(
    Message.created_at.desc()
).limit(20).all()
```

---

## Best Practices Summary

### Database
- ✅ Store ALL state in database
- ✅ Create proper indexes for performance
- ✅ Use foreign keys for data integrity
- ✅ Add created_at/updated_at timestamps

### Security
- ✅ ALWAYS filter queries by user_id
- ✅ Verify ownership before operations
- ✅ Use row-level security if available
- ✅ Never trust conversation_id from client

### Performance
- ✅ Limit conversation history (20-30 messages)
- ✅ Use database indexes
- ✅ Paginate conversation lists
- ✅ Consider caching for read-heavy workloads

### Architecture
- ✅ No server-side sessions
- ✅ No global state variables
- ✅ Create service instances per-request
- ✅ Every request fetches fresh from database

### Context Window
- ✅ Limit messages to prevent huge contexts
- ✅ Order by created_at for chronological order
- ✅ Fetch only what AI needs (not full history)
- ✅ Consider summarization for very long chats

---

## Deployment Considerations

### Horizontal Scaling

```
Stateless architecture enables easy scaling:

Request 1 → Server A → Database
Request 2 → Server B → Database  ← Different server, same data!
Request 3 → Server A → Database  ← Server A again, still works!

No session affinity needed!
No sticky sessions required!
```

### Container/Kubernetes

```yaml
# Can scale pods freely
apiVersion: apps/v1
kind: Deployment
spec:
  replicas: 5  # Run 5 instances
  # All instances are identical
  # No coordination needed
  # Database is single source of truth
```

### Serverless

```python
# Works perfectly with AWS Lambda, Cloud Functions, etc.
# Each invocation is fresh
# No state between invocations
# Database provides continuity
```

---

## Debugging

### Check Conversation State

```sql
-- View conversation and message counts
SELECT
    c.id,
    c.title,
    c.user_id,
    COUNT(m.id) as message_count,
    MAX(m.created_at) as last_message
FROM conversations c
LEFT JOIN messages m ON m.conversation_id = c.id
WHERE c.user_id = 1
GROUP BY c.id
ORDER BY last_message DESC;
```

### Monitor Database Queries

```python
# Enable SQLAlchemy query logging
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# See all queries in logs
# Identify slow queries
# Optimize with indexes
```

---

## Migration from Stateful to Stateless

### Before (Stateful)

```python
# Old code with sessions
conversations = {}  # Global dict

@app.post("/chat")
def chat(request, session):
    conv_id = session.get('conversation_id')
    conversation = conversations[conv_id]
    # ...
```

### After (Stateless)

```python
# New code with database
@app.post("/chat")
def chat(request, db, user):
    # Fetch from database
    conversation = db.query(Conversation).filter(
        Conversation.id == request.conversation_id,
        Conversation.user_id == user.id
    ).first()
    # ...
```

---

**Last Updated:** 2026-01-12
**Skill Version:** 1.0.0
**Recommended For:** Phase 3 AI Chatbot - Stateless Conversation Management
