"""
Chat router for AI-powered conversational task management.

Phase III: AI Chatbot
- Stateless architecture (all state in PostgreSQL)
- JWT authentication required
- User isolation enforced
- OpenAI Agent with MCP tools

Spec Reference: @specs/features/chatbot-features.md
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List
from datetime import datetime

from app.database import get_session
from app.models import User, Conversation, Message
from app.schemas import ChatMessageRequest, ChatMessageResponse
from app.auth import get_current_user
from app.ai.agent import get_agent, TODO_ASSISTANT_SYSTEM_PROMPT

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


# ============================================================================
# Helper Functions for Conversation Management
# ============================================================================


async def get_or_create_conversation(
    session: AsyncSession,
    user_id: str,
    conversation_id: int | None = None
) -> Conversation:
    """
    Get existing conversation or create new one.

    Stateless: Fetches from database on every request.

    Args:
        session: Database session
        user_id: User ID (for user isolation)
        conversation_id: Optional conversation ID

    Returns:
        Conversation object

    Raises:
        HTTPException: 404 if conversation not found or access denied
    """
    if conversation_id:
        # Get existing conversation
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id  # ✅ CRITICAL: User isolation
        )
        result = await session.execute(statement)
        conversation = result.scalar_one_or_none()

        if not conversation:
            logger.warning(
                f"Conversation {conversation_id} not found for user {user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or access denied"
            )

        # Update timestamp
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)

        logger.info(f"Retrieved conversation {conversation_id} for user {user_id}")
        return conversation
    else:
        # Create new conversation
        conversation = Conversation(
            user_id=user_id,
            title="New Conversation",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_active=True
        )
        session.add(conversation)
        await session.flush()  # Get conversation.id without committing

        logger.info(f"Created new conversation {conversation.id} for user {user_id}")
        return conversation


async def get_conversation_messages(
    session: AsyncSession,
    conversation_id: int,
    limit: int = 20
) -> List[Message]:
    """
    Get last N messages from conversation in chronological order.

    Stateless: Fetches fresh from database on every request.

    Args:
        session: Database session
        conversation_id: Conversation ID
        limit: Maximum messages to fetch (default: 20 for context window)

    Returns:
        List of messages in chronological order (oldest to newest)
    """
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )

    result = await session.execute(statement)
    messages = result.scalars().all()

    # Reverse to get chronological order (oldest to newest)
    messages_list = list(reversed(messages))

    logger.debug(
        f"Fetched {len(messages_list)} messages for conversation {conversation_id}"
    )
    return messages_list


async def store_message(
    session: AsyncSession,
    conversation_id: int,
    role: str,
    content: str
) -> Message:
    """
    Store a message in the database.

    Stateless: Persists immediately to database.

    Args:
        session: Database session
        conversation_id: Conversation ID
        role: Message role ("user", "assistant", "system", "tool")
        content: Message content

    Returns:
        Created message object
    """
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        created_at=datetime.utcnow()
    )
    session.add(message)

    logger.debug(f"Stored {role} message in conversation {conversation_id}")
    return message


# ============================================================================
# Chat Endpoint
# ============================================================================


@router.post("/message", response_model=ChatMessageResponse)
async def send_chat_message(
    request: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Process chat message with stateless architecture.

    Stateless Request Cycle (9 steps):
    1. Verify JWT and extract user_id (handled by dependency)
    2. Get or create conversation (from database)
    3. Fetch conversation history (last 20 messages from database)
    4. Store user message (to database)
    5. Build message array for AI
    6. Run OpenAI Agent with MCP tools
    7. Store assistant response (to database)
    8. Commit transaction
    9. Return response to client

    All state persists in PostgreSQL - server maintains NO memory.

    Phase III: AI Chatbot
    Spec Reference: @specs/features/chatbot-features.md - FR-009

    Args:
        request: Chat message request with message and optional conversation_id
        current_user: Current authenticated user (from JWT)
        session: Database session

    Returns:
        ChatMessageResponse with conversation_id and AI response

    Raises:
        HTTPException: 401 if unauthorized, 404 if conversation not found,
                      500 if AI service unavailable
    """
    user_id = current_user.id
    logger.info(
        f"Chat message request from user {user_id}, "
        f"conversation_id={request.conversation_id}"
    )

    try:
        # STEP 2: Get or create conversation (stateless - from DB)
        conversation = await get_or_create_conversation(
            session, user_id, request.conversation_id
        )

        # STEP 3: Fetch conversation history (stateless - last 20 messages from DB)
        messages_history = await get_conversation_messages(
            session, conversation.id, limit=20
        )

        # STEP 4: Store user message (to DB)
        await store_message(
            session, conversation.id, "user", request.message
        )

        # STEP 5: Build message array for AI
        message_array = [
            {"role": "system", "content": TODO_ASSISTANT_SYSTEM_PROMPT}
        ]

        # Add conversation history
        for msg in messages_history:
            message_array.append({
                "role": msg.role,
                "content": msg.content
            })

        # Add new user message
        message_array.append({
            "role": "user",
            "content": request.message
        })

        logger.debug(
            f"Message array built: {len(message_array)} messages "
            f"(including system prompt and new message)"
        )

        # STEP 6: Run OpenAI Agent with MCP tools
        agent = get_agent()
        try:
            response_text = await agent.run(
                messages=message_array,
                user_id=user_id,
                max_iterations=5
            )
            logger.info(
                f"Agent completed successfully for user {user_id}, "
                f"conversation {conversation.id}"
            )
        except Exception as e:
            logger.error(
                f"Agent execution failed for user {user_id}: {e}",
                exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="AI service is currently unavailable. Please try again later."
            )

        # STEP 7: Store assistant response (to DB)
        await store_message(
            session, conversation.id, "assistant", response_text
        )

        # STEP 8: Commit transaction (persist all changes to database)
        await session.commit()

        logger.info(
            f"Chat message processed successfully for user {user_id}, "
            f"conversation {conversation.id}"
        )

        # STEP 9: Return response to client
        return ChatMessageResponse(
            conversation_id=conversation.id,
            response=response_text
        )

    except HTTPException:
        # Re-raise HTTP exceptions (404, 500, etc.)
        raise
    except Exception as e:
        # Catch any unexpected errors
        logger.error(
            f"Unexpected error processing chat message for user {user_id}: {e}",
            exc_info=True
        )
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again."
        )
