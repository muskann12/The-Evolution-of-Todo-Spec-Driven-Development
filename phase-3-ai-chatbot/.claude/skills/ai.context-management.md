# Skill: AI Context Management

## Description
Manage conversation context and history for AI agents to maintain coherent, context-aware interactions across multiple turns. Implement smart context windowing, memory management, and conversation summarization for optimal AI performance.

## When to Use
- Building multi-turn conversational AI
- Managing long conversation histories
- Implementing context-aware responses
- Optimizing token usage for AI models
- Creating personalized AI experiences
- Handling conversation memory and recall

## Prerequisites
- Database for storing conversation history
- Understanding of token limits (GPT-4: 128K, GPT-4o: 128K)
- SQLAlchemy with async support
- Knowledge of conversation state management
- OpenAI API or similar LLM integration

---

## Core Concepts

### Context Window Management
- **Token Limits**: Models have maximum context windows
- **Sliding Window**: Keep recent messages, discard old ones
- **Summarization**: Compress old context into summaries
- **Selective Memory**: Keep important messages, discard noise

### Context Types
1. **Short-term Context**: Current conversation (last 10-20 messages)
2. **Medium-term Context**: Recent sessions (last few hours)
3. **Long-term Context**: User preferences, patterns (persistent)
4. **System Context**: User profile, settings, metadata

---

## Implementation

### 1. Database Models

```python
# models/conversation.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Conversation(Base):
    """
    Represents a conversation thread between user and AI.
    """
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=True)
    summary = Column(Text, nullable=True)  # AI-generated summary
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_archived = Column(Boolean, default=False)
    metadata = Column(JSON, default=dict)  # Store additional context

    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    user = relationship("User", back_populates="conversations")

    def __repr__(self):
        return f"<Conversation {self.id}: {self.title}>"


class Message(Base):
    """
    Individual message in a conversation.
    """
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user, assistant, system, tool
    content = Column(Text, nullable=True)
    tool_calls = Column(JSON, nullable=True)  # Tool executions
    metadata = Column(JSON, default=dict)  # Tokens, model, latency, etc.
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_summary = Column(Boolean, default=False)  # Mark summarized messages
    importance_score = Column(Integer, default=0)  # 0-10, for prioritization

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message {self.id}: {self.role}>"


class UserContext(Base):
    """
    Long-term user context and preferences.
    """
    __tablename__ = "user_contexts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    preferences = Column(JSON, default=dict)  # User preferences
    personality_traits = Column(JSON, default=dict)  # Learned traits
    common_tasks = Column(JSON, default=list)  # Frequently created tasks
    working_hours = Column(JSON, default=dict)  # Typical working hours
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<UserContext user={self.user_id}>"
```

### 2. Context Manager

```python
# agents/context_manager.py
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from models.conversation import Conversation, Message, UserContext
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ContextManager:
    """
    Manages conversation context, history, and memory.
    """

    MAX_TOKENS = 100000  # Reserve tokens for response
    TOKENS_PER_MESSAGE = 100  # Average estimate
    MAX_MESSAGES = 50  # Hard limit on messages

    def __init__(self, db: AsyncSession, user_id: int):
        self.db = db
        self.user_id = user_id

    async def create_conversation(
        self,
        title: Optional[str] = None
    ) -> Conversation:
        """Create a new conversation."""
        conversation = Conversation(
            user_id=self.user_id,
            title=title or f"Chat {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            metadata={}
        )
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)

        logger.info(f"Created conversation {conversation.id} for user {self.user_id}")
        return conversation

    async def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        tool_calls: Optional[List[Dict]] = None,
        metadata: Optional[Dict] = None,
        importance_score: int = 0
    ) -> Message:
        """Add a message to conversation."""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_calls=tool_calls,
            metadata=metadata or {},
            importance_score=importance_score
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)

        # Update conversation timestamp
        await self.db.execute(
            f"UPDATE conversations SET updated_at = :now WHERE id = :id",
            {"now": datetime.utcnow(), "id": conversation_id}
        )

        return message

    async def get_conversation_messages(
        self,
        conversation_id: int,
        limit: Optional[int] = None,
        include_system: bool = True
    ) -> List[Message]:
        """
        Get messages for a conversation.

        Args:
            conversation_id: Conversation ID
            limit: Maximum number of messages (None = all)
            include_system: Include system messages

        Returns:
            List of messages ordered by creation time
        """
        query = select(Message).where(Message.conversation_id == conversation_id)

        if not include_system:
            query = query.where(Message.role != "system")

        query = query.order_by(Message.created_at.asc())

        if limit:
            # Get most recent messages
            subquery = query.order_by(Message.created_at.desc()).limit(limit).subquery()
            query = select(Message).select_from(subquery).order_by(Message.created_at.asc())

        result = await self.db.execute(query)
        messages = result.scalars().all()

        return list(messages)

    async def get_context_window(
        self,
        conversation_id: int,
        max_tokens: Optional[int] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get optimized context window for AI model.

        Applies smart strategies:
        1. Keep recent messages
        2. Include conversation summary if exists
        3. Prioritize important messages
        4. Stay within token budget

        Args:
            conversation_id: Conversation ID
            max_tokens: Maximum tokens to use (default: MAX_TOKENS)

        Returns:
            Tuple of (messages_list, estimated_tokens)
        """
        max_tokens = max_tokens or self.MAX_TOKENS

        # Get conversation with summary
        conversation = await self.db.get(Conversation, conversation_id)

        # Get all messages
        all_messages = await self.get_conversation_messages(
            conversation_id,
            include_system=False
        )

        # Strategy 1: If conversation is short, return all
        if len(all_messages) <= 20:
            messages = self._messages_to_dict(all_messages)
            estimated_tokens = len(all_messages) * self.TOKENS_PER_MESSAGE
            return messages, estimated_tokens

        # Strategy 2: Use sliding window with summary
        messages = []

        # Add summary if exists
        if conversation.summary:
            messages.append({
                "role": "system",
                "content": f"Previous conversation summary: {conversation.summary}"
            })

        # Get recent messages (last 20)
        recent_messages = all_messages[-20:]
        messages.extend(self._messages_to_dict(recent_messages))

        # Calculate tokens
        estimated_tokens = len(messages) * self.TOKENS_PER_MESSAGE

        logger.info(
            f"Context window: {len(messages)} messages, ~{estimated_tokens} tokens"
        )

        return messages, estimated_tokens

    async def should_summarize(self, conversation_id: int) -> bool:
        """
        Check if conversation should be summarized.

        Criteria:
        - More than 30 messages
        - Last summary was > 20 messages ago
        """
        query = select(func.count(Message.id)).where(
            Message.conversation_id == conversation_id
        )
        result = await self.db.execute(query)
        message_count = result.scalar()

        if message_count < 30:
            return False

        # Check last summary
        conversation = await self.db.get(Conversation, conversation_id)
        if not conversation.summary:
            return True

        # Get messages since last summary
        query = select(func.count(Message.id)).where(
            and_(
                Message.conversation_id == conversation_id,
                Message.is_summary == False,
                Message.created_at > conversation.updated_at
            )
        )
        result = await self.db.execute(query)
        new_messages = result.scalar()

        return new_messages > 20

    async def summarize_conversation(
        self,
        conversation_id: int,
        ai_agent
    ) -> str:
        """
        Generate summary of conversation using AI.

        Args:
            conversation_id: Conversation ID
            ai_agent: OpenAI agent instance

        Returns:
            Summary text
        """
        # Get all messages
        messages = await self.get_conversation_messages(conversation_id)

        # Build summary prompt
        conversation_text = "\n".join([
            f"{msg.role}: {msg.content}"
            for msg in messages
            if msg.content and not msg.is_summary
        ])

        summary_prompt = f"""Summarize this conversation concisely. Focus on:
- Key tasks discussed
- Important decisions made
- User preferences mentioned
- Action items

Conversation:
{conversation_text}

Provide a brief summary (3-5 sentences):"""

        # Generate summary using AI
        from openai import AsyncOpenAI
        import os

        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = await client.chat.completions.create(
            model="gpt-4o-mini",  # Use cheaper model for summaries
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes conversations."},
                {"role": "user", "content": summary_prompt}
            ],
            max_tokens=200,
            temperature=0.5
        )

        summary = response.choices[0].message.content

        # Update conversation with summary
        conversation = await self.db.get(Conversation, conversation_id)
        conversation.summary = summary
        conversation.updated_at = datetime.utcnow()
        await self.db.commit()

        logger.info(f"Summarized conversation {conversation_id}")

        return summary

    async def get_user_context(self) -> Optional[UserContext]:
        """Get long-term user context."""
        query = select(UserContext).where(UserContext.user_id == self.user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_user_context(
        self,
        preferences: Optional[Dict] = None,
        personality_traits: Optional[Dict] = None,
        common_tasks: Optional[List] = None
    ) -> UserContext:
        """Update user context."""
        context = await self.get_user_context()

        if not context:
            context = UserContext(user_id=self.user_id)
            self.db.add(context)

        if preferences:
            context.preferences.update(preferences)
        if personality_traits:
            context.personality_traits.update(personality_traits)
        if common_tasks:
            context.common_tasks = common_tasks

        context.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(context)

        return context

    async def get_recent_conversations(
        self,
        limit: int = 10
    ) -> List[Conversation]:
        """Get user's recent conversations."""
        query = (
            select(Conversation)
            .where(Conversation.user_id == self.user_id)
            .where(Conversation.is_archived == False)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def archive_conversation(self, conversation_id: int):
        """Archive a conversation."""
        conversation = await self.db.get(Conversation, conversation_id)
        if conversation and conversation.user_id == self.user_id:
            conversation.is_archived = True
            await self.db.commit()

    def _messages_to_dict(self, messages: List[Message]) -> List[Dict[str, Any]]:
        """Convert Message objects to OpenAI format."""
        return [
            {
                "role": msg.role,
                "content": msg.content or "",
                **({"tool_calls": msg.tool_calls} if msg.tool_calls else {})
            }
            for msg in messages
        ]

    async def calculate_importance_score(
        self,
        message: Message,
        conversation: Conversation
    ) -> int:
        """
        Calculate importance score for a message (0-10).

        Factors:
        - Tool calls (high importance)
        - Keywords (task, important, urgent)
        - User questions
        - Error messages
        """
        score = 0

        if message.tool_calls:
            score += 5  # Tool interactions are important

        if message.role == "user":
            score += 2  # User messages more important than assistant

        # Check for important keywords
        content_lower = (message.content or "").lower()
        important_keywords = ["important", "urgent", "critical", "asap", "deadline"]

        if any(keyword in content_lower for keyword in important_keywords):
            score += 2

        # Questions are important
        if "?" in (message.content or ""):
            score += 1

        return min(score, 10)  # Cap at 10
```

### 3. Enhanced Chat API with Context Management

```python
# routes/chat.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.auth import get_current_user
from agents.openai_agent import OpenAIAgent, AgentConfig
from agents.tools import get_mcp_tools
from agents.prompts import TODO_ASSISTANT_PROMPT
from agents.context_manager import ContextManager

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: int
    tool_calls: List[dict] = []
    tokens_used: Optional[int] = None


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Chat with AI agent using context management.
    """
    # Initialize context manager
    context_mgr = ContextManager(db, current_user.id)

    # Get or create conversation
    if request.conversation_id:
        conversation_id = request.conversation_id
        # TODO: Verify user owns conversation
    else:
        conversation = await context_mgr.create_conversation()
        conversation_id = conversation.id

    # Add user message
    await context_mgr.add_message(
        conversation_id=conversation_id,
        role="user",
        content=request.message,
        importance_score=5  # User messages default to medium importance
    )

    # Check if we should summarize
    if await context_mgr.should_summarize(conversation_id):
        agent = OpenAIAgent()
        await context_mgr.summarize_conversation(conversation_id, agent)

    # Get optimized context window
    messages, estimated_tokens = await context_mgr.get_context_window(
        conversation_id,
        max_tokens=100000
    )

    # Get user context for personalization
    user_context = await context_mgr.get_user_context()

    # Enhance system prompt with user context
    enhanced_prompt = TODO_ASSISTANT_PROMPT
    if user_context and user_context.preferences:
        enhanced_prompt += f"\n\nUser preferences: {user_context.preferences}"

    # Initialize agent
    config = AgentConfig(model="gpt-4o", temperature=0.7)
    agent = OpenAIAgent(config=config, system_prompt=enhanced_prompt)

    # Register tools
    tools = get_mcp_tools()
    await agent.register_tools(tools)

    # Run agent
    response, tool_calls = await agent.run(
        messages=messages,
        user_id=current_user.id
    )

    # Calculate importance score for assistant message
    importance = 3  # Default
    if tool_calls:
        importance = 7  # High importance if tools were used

    # Store assistant response
    await context_mgr.add_message(
        conversation_id=conversation_id,
        role="assistant",
        content=response,
        tool_calls=tool_calls if tool_calls else None,
        importance_score=importance
    )

    return ChatResponse(
        response=response,
        conversation_id=conversation_id,
        tool_calls=tool_calls,
        tokens_used=estimated_tokens
    )
```

### 4. Context-Aware System Prompts

```python
# agents/prompts.py

def build_context_aware_prompt(
    user_context: Optional[Dict] = None,
    conversation_summary: Optional[str] = None
) -> str:
    """
    Build system prompt with user context and conversation summary.
    """
    base_prompt = """You are an AI assistant for TODO management.

Your capabilities:
- Create, read, update, delete tasks
- Search and filter tasks
- Provide insights and analytics

Your behavior:
- Be concise and helpful
- Remember context from this conversation
- Use user preferences when available
"""

    # Add conversation summary
    if conversation_summary:
        base_prompt += f"""

## Previous Conversation
{conversation_summary}

Continue from where we left off. Reference previous topics when relevant.
"""

    # Add user context
    if user_context:
        preferences = user_context.get("preferences", {})

        if preferences:
            base_prompt += f"""

## User Preferences
"""
            if preferences.get("default_priority"):
                base_prompt += f"- Default task priority: {preferences['default_priority']}\n"

            if preferences.get("work_hours"):
                base_prompt += f"- Working hours: {preferences['work_hours']}\n"

            if preferences.get("preferred_tags"):
                base_prompt += f"- Common tags: {', '.join(preferences['preferred_tags'])}\n"

    return base_prompt
```

---

## Token Management

### Token Estimation

```python
# utils/token_counter.py
import tiktoken

class TokenCounter:
    """Estimate token counts for OpenAI models."""

    def __init__(self, model: str = "gpt-4o"):
        self.encoding = tiktoken.encoding_for_model(model)

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoding.encode(text))

    def count_messages(self, messages: List[Dict]) -> int:
        """Count tokens in message list."""
        total = 0
        for message in messages:
            # Every message has overhead
            total += 4  # Message wrapper tokens

            for key, value in message.items():
                if isinstance(value, str):
                    total += self.count_tokens(value)

        total += 2  # Conversation wrapper
        return total

    def fits_in_context(
        self,
        messages: List[Dict],
        max_tokens: int = 128000
    ) -> bool:
        """Check if messages fit in context window."""
        return self.count_messages(messages) < max_tokens
```

---

## Best Practices

### 1. Always Stay Within Token Budget
```python
# ✅ Check token count before API call
if token_counter.fits_in_context(messages, max_tokens=100000):
    response = await agent.run(messages)
else:
    # Summarize or truncate
    await context_mgr.summarize_conversation(conversation_id)
```

### 2. Summarize Long Conversations
```python
# ✅ Auto-summarize after 30 messages
if await context_mgr.should_summarize(conversation_id):
    summary = await context_mgr.summarize_conversation(conversation_id, agent)
```

### 3. Prioritize Important Messages
```python
# ✅ Keep important messages, discard trivial ones
messages = await context_mgr.get_important_messages(
    conversation_id,
    min_importance=5
)
```

### 4. Store User Preferences
```python
# ✅ Learn from user behavior
if "high priority" in user_messages:
    await context_mgr.update_user_context(
        preferences={"default_priority": "high"}
    )
```

### 5. Use Efficient Models for Summaries
```python
# ✅ Use cheaper model for background tasks
summary = await generate_summary(
    messages,
    model="gpt-4o-mini"  # Cheaper than gpt-4o
)
```

---

## Testing

```python
# tests/test_context_manager.py
import pytest
from agents.context_manager import ContextManager

@pytest.mark.asyncio
async def test_context_window_limits(db_session, test_user):
    """Test context window stays within limits."""
    context_mgr = ContextManager(db_session, test_user.id)

    conversation = await context_mgr.create_conversation()

    # Add 100 messages
    for i in range(100):
        await context_mgr.add_message(
            conversation.id,
            role="user" if i % 2 == 0 else "assistant",
            content=f"Message {i}"
        )

    # Get context window
    messages, tokens = await context_mgr.get_context_window(
        conversation.id,
        max_tokens=10000
    )

    # Should limit messages to fit tokens
    assert tokens < 10000
    assert len(messages) < 100  # Should not include all 100

@pytest.mark.asyncio
async def test_summarization(db_session, test_user):
    """Test conversation summarization."""
    context_mgr = ContextManager(db_session, test_user.id)

    conversation = await context_mgr.create_conversation()

    # Add many messages
    for i in range(35):
        await context_mgr.add_message(
            conversation.id,
            role="user",
            content=f"Create task {i}"
        )

    # Should need summarization
    assert await context_mgr.should_summarize(conversation.id)
```

---

**Last Updated:** 2026-01-12
**Skill Version:** 1.0.0
**Recommended For:** Phase 3 AI Chatbot - Context Management
