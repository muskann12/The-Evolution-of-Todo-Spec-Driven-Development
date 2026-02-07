# Skill: AI Smart Prioritization

## Description
Implement AI-powered intelligent task prioritization that automatically suggests priority levels based on task content, context, deadlines, and user patterns. Help users focus on what matters most through smart priority scoring and recommendations.

## When to Use
- Auto-suggesting task priorities during creation
- Re-prioritizing existing tasks based on context
- Identifying urgent vs important tasks
- Optimizing task ordering for maximum productivity
- Detecting priority conflicts or overload
- Providing priority justifications

## Prerequisites
- OpenAI API or similar LLM
- Task history and completion patterns
- User context and preferences
- Understanding of priority frameworks (Eisenhower Matrix, etc.)
- Access to calendar/deadline information

---

## Core Concepts

### Priority Frameworks

1. **Eisenhower Matrix**
   - Urgent + Important = High Priority
   - Important but Not Urgent = Medium Priority
   - Urgent but Not Important = Medium/Low Priority
   - Neither = Low Priority

2. **Impact vs Effort**
   - High Impact + Low Effort = Quick wins (High)
   - High Impact + High Effort = Major projects (High)
   - Low Impact + Low Effort = Fill-ins (Low)
   - Low Impact + High Effort = Time wasters (Low)

3. **Time-based Priority**
   - Deadline proximity
   - Dependencies on other tasks
   - Blocking others' work
   - Recurring patterns

### AI Priority Scoring Components

1. **Deadline Analysis**: How soon is it due?
2. **Keyword Detection**: Urgent, important, critical, etc.
3. **Historical Patterns**: What user prioritized before
4. **Context Awareness**: Time of day, current workload
5. **Impact Assessment**: Consequences of delay
6. **Effort Estimation**: How long will it take?

---

## Implementation

### 1. Priority Analyzer Service

```python
# services/priority_analyzer.py
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import re
from openai import AsyncOpenAI
import os
import json

class PriorityAnalyzer:
    """
    Analyze tasks and suggest optimal priorities using AI.
    """

    # Keywords that indicate priority
    URGENT_KEYWORDS = [
        "urgent", "asap", "immediately", "critical", "emergency",
        "deadline", "today", "now", "rush"
    ]

    IMPORTANT_KEYWORDS = [
        "important", "crucial", "essential", "vital", "key",
        "significant", "major", "primary"
    ]

    LOW_PRIORITY_KEYWORDS = [
        "when possible", "sometime", "eventually", "maybe",
        "nice to have", "optional", "low priority"
    ]

    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def suggest_priority(
        self,
        title: str,
        description: Optional[str] = None,
        due_date: Optional[datetime] = None,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Suggest priority for a task using multiple factors.

        Args:
            title: Task title
            description: Task description
            due_date: Task due date
            context: Additional context (user patterns, current workload, etc.)

        Returns:
            Dict with suggested priority and reasoning
        """
        # Rule-based scoring first
        rule_score = self._rule_based_scoring(
            title,
            description,
            due_date
        )

        # AI-enhanced scoring
        ai_score = await self._ai_priority_scoring(
            title,
            description,
            due_date,
            context
        )

        # Combine scores (70% AI, 30% rules)
        final_score = (ai_score["score"] * 0.7) + (rule_score["score"] * 0.3)

        # Map score to priority
        if final_score >= 7:
            priority = "high"
        elif final_score >= 4:
            priority = "medium"
        else:
            priority = "low"

        return {
            "priority": priority,
            "confidence": ai_score.get("confidence", 0.5),
            "score": final_score,
            "reasoning": ai_score.get("reasoning", rule_score["reasoning"]),
            "factors": {
                "rule_based": rule_score,
                "ai_enhanced": ai_score
            }
        }

    def _rule_based_scoring(
        self,
        title: str,
        description: Optional[str],
        due_date: Optional[datetime]
    ) -> Dict[str, Any]:
        """
        Calculate priority score using rule-based heuristics.

        Returns:
            Dict with score (0-10) and reasoning
        """
        score = 5.0  # Start neutral
        reasons = []

        text = f"{title} {description or ''}".lower()

        # Check for urgent keywords
        urgent_count = sum(1 for keyword in self.URGENT_KEYWORDS if keyword in text)
        if urgent_count > 0:
            score += min(urgent_count * 2, 3)
            reasons.append(f"Contains {urgent_count} urgency indicator(s)")

        # Check for important keywords
        important_count = sum(1 for keyword in self.IMPORTANT_KEYWORDS if keyword in text)
        if important_count > 0:
            score += min(important_count * 1.5, 2)
            reasons.append(f"Contains {important_count} importance indicator(s)")

        # Check for low priority keywords
        low_count = sum(1 for keyword in self.LOW_PRIORITY_KEYWORDS if keyword in text)
        if low_count > 0:
            score -= min(low_count * 2, 3)
            reasons.append(f"Contains {low_count} low priority indicator(s)")

        # Deadline proximity
        if due_date:
            days_until = (due_date - datetime.utcnow()).days

            if days_until < 0:
                score += 4
                reasons.append("Overdue!")
            elif days_until == 0:
                score += 3
                reasons.append("Due today")
            elif days_until == 1:
                score += 2.5
                reasons.append("Due tomorrow")
            elif days_until <= 3:
                score += 2
                reasons.append(f"Due in {days_until} days")
            elif days_until <= 7:
                score += 1
                reasons.append(f"Due in {days_until} days")

        # Clamp score to 0-10
        score = max(0, min(10, score))

        return {
            "score": score,
            "reasoning": "; ".join(reasons) if reasons else "Standard priority"
        }

    async def _ai_priority_scoring(
        self,
        title: str,
        description: Optional[str],
        due_date: Optional[datetime],
        context: Optional[Dict]
    ) -> Dict[str, Any]:
        """
        Use AI to analyze and score task priority.

        Returns:
            Dict with score, confidence, and reasoning
        """
        # Build context
        current_time = datetime.utcnow()
        time_context = f"Current time: {current_time.strftime('%A, %B %d, %Y %I:%M %p')}"

        due_context = ""
        if due_date:
            days_until = (due_date - current_time).days
            due_context = f"Due date: {due_date.strftime('%B %d, %Y')} ({days_until} days from now)"

        workload_context = ""
        if context and "workload" in context:
            workload = context["workload"]
            workload_context = f"""
Current workload:
- Total active tasks: {workload.get('total_active', 0)}
- High priority tasks: {workload.get('high_priority_incomplete', 0)}
- Overdue tasks: {workload.get('overdue', 0)}
"""

        prompt = f"""Analyze this task and suggest a priority level.

## Task
Title: {title}
Description: {description or 'No description'}
{due_context}

## Context
{time_context}
{workload_context}

## Priority Framework
Consider:
1. **Urgency**: How time-sensitive is this?
2. **Importance**: What's the impact if this isn't done?
3. **Effort**: Is this a quick win or major project?
4. **Dependencies**: Does this block other work?
5. **Deadline proximity**: How close is the deadline?

## Your Task
Score the priority from 0-10 where:
- 0-3: Low priority (can wait, not urgent)
- 4-6: Medium priority (important but not urgent)
- 7-10: High priority (urgent and/or critical)

Respond in JSON format:
{{
  "score": 7.5,
  "confidence": 0.85,
  "reasoning": "This task is high priority because...",
  "urgency_level": "high/medium/low",
  "importance_level": "high/medium/low",
  "recommended_priority": "high/medium/low"
}}
"""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",  # Cheaper model is fine for this
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at prioritization and task management. Analyze tasks objectively and provide clear reasoning."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent scoring
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            # Fallback to rule-based if AI fails
            return {
                "score": 5.0,
                "confidence": 0.5,
                "reasoning": f"AI analysis unavailable ({str(e)}), using default",
                "recommended_priority": "medium"
            }

    async def batch_prioritize(
        self,
        tasks: List[Dict],
        context: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Prioritize multiple tasks and suggest optimal ordering.

        Args:
            tasks: List of tasks to prioritize
            context: Context about user and workload

        Returns:
            List of tasks with suggested priorities
        """
        results = []

        for task in tasks:
            priority_suggestion = await self.suggest_priority(
                title=task["title"],
                description=task.get("description"),
                due_date=datetime.fromisoformat(task["due_date"]) if task.get("due_date") else None,
                context=context
            )

            results.append({
                "task_id": task["id"],
                "title": task["title"],
                "current_priority": task.get("priority", "medium"),
                "suggested_priority": priority_suggestion["priority"],
                "score": priority_suggestion["score"],
                "reasoning": priority_suggestion["reasoning"],
                "should_change": task.get("priority") != priority_suggestion["priority"]
            })

        # Sort by score (highest first)
        results.sort(key=lambda x: x["score"], reverse=True)

        return results

    async def detect_priority_conflicts(
        self,
        tasks: List[Dict]
    ) -> Dict[str, Any]:
        """
        Detect if user has too many high priority tasks.

        Returns:
            Analysis of priority distribution and recommendations
        """
        # Count by priority
        high_count = sum(1 for t in tasks if t.get("priority") == "high")
        medium_count = sum(1 for t in tasks if t.get("priority") == "medium")
        low_count = sum(1 for t in tasks if t.get("priority") == "low")

        total = len(tasks)

        # Ideal distribution: 20% high, 50% medium, 30% low
        high_pct = (high_count / total * 100) if total > 0 else 0
        medium_pct = (medium_count / total * 100) if total > 0 else 0
        low_pct = (low_count / total * 100) if total > 0 else 0

        issues = []
        recommendations = []

        # Check for too many high priority tasks
        if high_pct > 40:
            issues.append(f"Too many high priority tasks ({high_count}/{total})")
            recommendations.append(
                "Consider re-evaluating some tasks. "
                "Not everything can be highest priority."
            )

        # Check for no high priority tasks
        if high_count == 0 and total > 5:
            issues.append("No high priority tasks defined")
            recommendations.append(
                "Identify your most important tasks and mark them as high priority."
            )

        # Check for priority inflation
        if high_pct > 50:
            issues.append("Priority inflation detected")
            recommendations.append(
                "When everything is high priority, nothing is. "
                "Use medium and low priorities more."
            )

        return {
            "total_tasks": total,
            "distribution": {
                "high": {"count": high_count, "percentage": round(high_pct, 1)},
                "medium": {"count": medium_count, "percentage": round(medium_pct, 1)},
                "low": {"count": low_count, "percentage": round(low_pct, 1)}
            },
            "ideal_distribution": {
                "high": "20%",
                "medium": "50%",
                "low": "30%"
            },
            "has_issues": len(issues) > 0,
            "issues": issues,
            "recommendations": recommendations
        }
```

### 2. Priority API Endpoints

```python
# routes/priority.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.database import get_db
from app.auth import get_current_user
from app.models import Todo
from services.priority_analyzer import PriorityAnalyzer
from services.task_analytics import TaskAnalyticsService

router = APIRouter(prefix="/api/priority", tags=["priority"])


class PrioritySuggestionRequest(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None


class PrioritySuggestionResponse(BaseModel):
    priority: str
    confidence: float
    score: float
    reasoning: str


class BatchPrioritizeRequest(BaseModel):
    task_ids: List[int]


@router.post("/suggest", response_model=PrioritySuggestionResponse)
async def suggest_priority(
    request: PrioritySuggestionRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get AI-powered priority suggestion for a task.
    """
    analyzer = PriorityAnalyzer()
    analytics = TaskAnalyticsService(db, current_user.id)

    # Get context
    workload = await analytics.get_workload_distribution()

    # Parse due date if provided
    due_date = None
    if request.due_date:
        try:
            due_date = datetime.fromisoformat(request.due_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid due_date format")

    # Get suggestion
    suggestion = await analyzer.suggest_priority(
        title=request.title,
        description=request.description,
        due_date=due_date,
        context={"workload": workload}
    )

    return PrioritySuggestionResponse(**suggestion)


@router.post("/batch-prioritize")
async def batch_prioritize_tasks(
    request: BatchPrioritizeRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Re-prioritize multiple tasks at once.
    """
    analyzer = PriorityAnalyzer()
    analytics = TaskAnalyticsService(db, current_user.id)

    # Get tasks
    query = select(Todo).where(
        and_(
            Todo.user_id == current_user.id,
            Todo.id.in_(request.task_ids)
        )
    )

    result = await db.execute(query)
    tasks = result.scalars().all()

    if len(tasks) != len(request.task_ids):
        raise HTTPException(status_code=404, detail="Some tasks not found")

    # Convert to dict
    task_dicts = [
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "priority": t.priority,
            "due_date": t.due_date.isoformat() if t.due_date else None
        }
        for t in tasks
    ]

    # Get workload context
    workload = await analytics.get_workload_distribution()

    # Batch prioritize
    results = await analyzer.batch_prioritize(
        task_dicts,
        context={"workload": workload}
    )

    return {
        "total_analyzed": len(results),
        "tasks": results,
        "changes_recommended": sum(1 for r in results if r["should_change"])
    }


@router.get("/conflicts")
async def detect_priority_conflicts(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Detect priority conflicts and imbalances.
    """
    analyzer = PriorityAnalyzer()

    # Get all active tasks
    query = select(Todo).where(
        and_(
            Todo.user_id == current_user.id,
            Todo.status != "done"
        )
    )

    result = await db.execute(query)
    tasks = result.scalars().all()

    # Convert to dict
    task_dicts = [
        {
            "id": t.id,
            "title": t.title,
            "priority": t.priority,
            "status": t.status
        }
        for t in tasks
    ]

    # Analyze conflicts
    analysis = await analyzer.detect_priority_conflicts(task_dicts)

    return analysis


@router.post("/auto-prioritize")
async def auto_prioritize_all(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Automatically re-prioritize all tasks (use with caution).
    """
    analyzer = PriorityAnalyzer()
    analytics = TaskAnalyticsService(db, current_user.id)

    # Get all incomplete tasks
    query = select(Todo).where(
        and_(
            Todo.user_id == current_user.id,
            Todo.status != "done"
        )
    )

    result = await db.execute(query)
    tasks = result.scalars().all()

    # Convert to dict
    task_dicts = [
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "priority": t.priority,
            "due_date": t.due_date.isoformat() if t.due_date else None
        }
        for t in tasks
    ]

    # Get workload
    workload = await analytics.get_workload_distribution()

    # Batch prioritize
    results = await analyzer.batch_prioritize(
        task_dicts,
        context={"workload": workload}
    )

    # Update tasks
    updated_count = 0
    for result_item in results:
        if result_item["should_change"]:
            task = await db.get(Todo, result_item["task_id"])
            if task:
                task.priority = result_item["suggested_priority"]
                updated_count += 1

    await db.commit()

    return {
        "total_analyzed": len(results),
        "updated": updated_count,
        "results": results
    }
```

### 3. Frontend Priority Suggestion Component

```typescript
// components/priority/PrioritySuggestion.tsx
'use client'

import React, { useEffect, useState } from 'react'
import { AlertCircle, TrendingUp, Info } from 'lucide-react'

interface PrioritySuggestionProps {
  title: string
  description?: string
  dueDate?: string
  onSuggestion?: (priority: string) => void
}

interface Suggestion {
  priority: string
  confidence: number
  score: number
  reasoning: string
}

export function PrioritySuggestion({
  title,
  description,
  dueDate,
  onSuggestion
}: PrioritySuggestionProps) {
  const [suggestion, setSuggestion] = useState<Suggestion | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    // Auto-fetch suggestion when title changes
    if (title.length > 5) {
      fetchSuggestion()
    }
  }, [title, description, dueDate])

  const fetchSuggestion = async () => {
    setIsLoading(true)

    try {
      const response = await fetch('/api/priority/suggest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ title, description, due_date: dueDate })
      })

      const data = await response.json()
      setSuggestion(data)

      if (onSuggestion) {
        onSuggestion(data.priority)
      }
    } catch (error) {
      console.error('Failed to fetch priority suggestion:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (!suggestion && !isLoading) {
    return null
  }

  const priorityColors = {
    high: 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-300 border-red-300 dark:border-red-700',
    medium: 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-700 dark:text-yellow-300 border-yellow-300 dark:border-yellow-700',
    low: 'bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-300 border-green-300 dark:border-green-700'
  }

  return (
    <div className="mt-2">
      {isLoading ? (
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600" />
          <span>Analyzing priority...</span>
        </div>
      ) : suggestion ? (
        <div className={`border rounded-lg p-3 ${priorityColors[suggestion.priority as keyof typeof priorityColors]}`}>
          <div className="flex items-start gap-2">
            <AlertCircle size={18} className="mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="font-semibold text-sm">
                  Suggested Priority: {suggestion.priority.toUpperCase()}
                </span>
                <span className="text-xs opacity-75">
                  (Confidence: {Math.round(suggestion.confidence * 100)}%)
                </span>
              </div>
              <p className="text-sm opacity-90">
                {suggestion.reasoning}
              </p>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  )
}
```

---

## Best Practices

### 1. Balance AI with Rules
```python
# ✅ Combine AI analysis with rule-based scoring
final_score = (ai_score * 0.7) + (rule_score * 0.3)
```

### 2. Explain Priority Decisions
```python
# ✅ Always provide reasoning
{
  "priority": "high",
  "reasoning": "Due tomorrow + contains 'urgent' keyword"
}
```

### 3. Use Cheaper Models
```python
# ✅ Priority analysis works fine with gpt-4o-mini
model = "gpt-4o-mini"  # Much cheaper than gpt-4o
```

### 4. Cache Suggestions
```python
# ✅ Cache priority suggestions to avoid redundant API calls
@lru_cache(maxsize=200)
def get_priority_suggestion(title: str, due_date: str):
    ...
```

### 5. Validate Priority Distribution
```python
# ✅ Warn users about priority inflation
if high_priority_pct > 40:
    warn("Too many high priority tasks")
```

---

## Testing

```python
# tests/test_priority_analyzer.py
import pytest
from services.priority_analyzer import PriorityAnalyzer
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_urgent_keyword_detection():
    """Test that urgent keywords increase priority."""
    analyzer = PriorityAnalyzer()

    result = analyzer._rule_based_scoring(
        title="URGENT: Fix production bug",
        description=None,
        due_date=None
    )

    assert result["score"] > 5  # Should be above neutral
    assert "urgency" in result["reasoning"].lower()

@pytest.mark.asyncio
async def test_deadline_proximity():
    """Test that close deadlines increase priority."""
    analyzer = PriorityAnalyzer()

    tomorrow = datetime.utcnow() + timedelta(days=1)

    result = analyzer._rule_based_scoring(
        title="Regular task",
        description=None,
        due_date=tomorrow
    )

    assert result["score"] > 6  # Should be high priority
    assert "tomorrow" in result["reasoning"].lower()
```

---

**Last Updated:** 2026-01-12
**Skill Version:** 1.0.0
**Recommended For:** Phase 3 AI Chatbot - Smart Prioritization
