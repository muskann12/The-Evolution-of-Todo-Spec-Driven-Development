# Skill: AI Task Suggestions

## Description
Implement AI-powered intelligent task suggestions and recommendations based on user behavior, patterns, task history, and context. Help users discover what to work on next, identify forgotten tasks, and optimize their productivity.

## When to Use
- Providing proactive task recommendations
- Suggesting next tasks to work on
- Identifying overdue or forgotten tasks
- Recommending task breakdowns
- Offering productivity insights
- Creating smart task templates

## Prerequisites
- User task history in database
- AI model access (OpenAI GPT-4o or similar)
- Task analytics and patterns
- User behavior tracking
- Context about current time, day, workload

---

## Core Concepts

### Suggestion Types

1. **Next Task Suggestions**: What should I work on next?
2. **Missing Tasks**: Tasks user might have forgotten
3. **Task Breakdown**: Suggest subtasks for large tasks
4. **Recurring Patterns**: Suggest tasks based on history
5. **Related Tasks**: Tasks that often go together
6. **Time-based**: Suggestions based on time of day/week

### Recommendation Engine Components

1. **Pattern Recognition**: Learn from user's task patterns
2. **Context Awareness**: Consider time, day, existing tasks
3. **Priority Weighting**: Balance urgency vs importance
4. **User Preferences**: Respect user's working style
5. **Smart Prompts**: Generate contextual AI suggestions

---

## Implementation

### 1. Task Analytics Service

```python
# services/task_analytics.py
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from datetime import datetime, timedelta
from collections import Counter
from app.models import Todo

class TaskAnalyticsService:
    """Analyze user's task patterns and behavior."""

    def __init__(self, db: AsyncSession, user_id: int):
        self.db = db
        self.user_id = user_id

    async def get_completion_patterns(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze when user typically completes tasks.

        Returns:
            Dict with completion patterns (by hour, by day, etc.)
        """
        date_from = datetime.utcnow() - timedelta(days=days)

        query = select(Todo).where(
            and_(
                Todo.user_id == self.user_id,
                Todo.status == "done",
                Todo.updated_at >= date_from
            )
        )

        result = await self.db.execute(query)
        completed_tasks = result.scalars().all()

        # Analyze by hour of day
        hours = [task.updated_at.hour for task in completed_tasks]
        hour_distribution = Counter(hours)

        # Analyze by day of week
        days_of_week = [task.updated_at.weekday() for task in completed_tasks]
        day_distribution = Counter(days_of_week)

        # Most productive hours
        most_productive_hours = sorted(
            hour_distribution.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]

        return {
            "total_completed": len(completed_tasks),
            "by_hour": dict(hour_distribution),
            "by_day": dict(day_distribution),
            "most_productive_hours": [h[0] for h in most_productive_hours],
            "avg_completion_time": self._calculate_avg_completion_time(completed_tasks)
        }

    async def get_common_task_patterns(self) -> List[Dict[str, Any]]:
        """
        Identify common task patterns and templates.

        Returns:
            List of common task patterns
        """
        query = select(Todo).where(
            and_(
                Todo.user_id == self.user_id,
                Todo.created_at >= datetime.utcnow() - timedelta(days=90)
            )
        )

        result = await self.db.execute(query)
        tasks = result.scalars().all()

        # Analyze common keywords in titles
        all_words = []
        for task in tasks:
            words = task.title.lower().split()
            all_words.extend(words)

        common_words = Counter(all_words).most_common(10)

        # Analyze common tag combinations
        tag_combinations = []
        for task in tasks:
            if task.tags:
                tag_combinations.append(tuple(sorted(task.tags)))

        common_tag_combos = Counter(tag_combinations).most_common(5)

        # Find recurring task titles (similar tasks)
        title_patterns = self._find_similar_titles([t.title for t in tasks])

        return {
            "common_keywords": [word for word, _ in common_words],
            "common_tag_combinations": [
                list(tags) for tags, _ in common_tag_combos
            ],
            "recurring_patterns": title_patterns
        }

    async def get_forgotten_tasks(self) -> List[Todo]:
        """
        Find tasks that might have been forgotten.

        Criteria:
        - Created > 7 days ago
        - Not completed
        - No recent activity
        - Not in 'done' status
        """
        seven_days_ago = datetime.utcnow() - timedelta(days=7)

        query = select(Todo).where(
            and_(
                Todo.user_id == self.user_id,
                Todo.created_at < seven_days_ago,
                Todo.status != "done",
                or_(
                    Todo.updated_at < seven_days_ago,
                    Todo.updated_at == None
                )
            )
        ).order_by(Todo.created_at.asc()).limit(10)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_overdue_tasks(self) -> List[Todo]:
        """Get tasks past their due date."""
        now = datetime.utcnow()

        query = select(Todo).where(
            and_(
                Todo.user_id == self.user_id,
                Todo.due_date < now,
                Todo.status != "done"
            )
        ).order_by(Todo.due_date.asc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_workload_distribution(self) -> Dict[str, Any]:
        """
        Analyze current workload distribution.
        """
        query = select(Todo).where(
            and_(
                Todo.user_id == self.user_id,
                Todo.status != "done"
            )
        )

        result = await self.db.execute(query)
        active_tasks = result.scalars().all()

        # By priority
        by_priority = Counter([t.priority for t in active_tasks])

        # By status
        by_status = Counter([t.status for t in active_tasks])

        # With due dates
        with_due_dates = sum(1 for t in active_tasks if t.due_date)
        overdue = sum(
            1 for t in active_tasks
            if t.due_date and t.due_date < datetime.utcnow()
        )

        return {
            "total_active": len(active_tasks),
            "by_priority": dict(by_priority),
            "by_status": dict(by_status),
            "with_due_dates": with_due_dates,
            "overdue": overdue,
            "high_priority_incomplete": by_priority.get("high", 0)
        }

    def _calculate_avg_completion_time(self, tasks: List[Todo]) -> float:
        """Calculate average time to complete tasks (in days)."""
        completion_times = []

        for task in tasks:
            if task.created_at and task.updated_at:
                delta = (task.updated_at - task.created_at).total_seconds()
                days = delta / (24 * 3600)
                completion_times.append(days)

        return sum(completion_times) / len(completion_times) if completion_times else 0

    def _find_similar_titles(self, titles: List[str]) -> List[str]:
        """Find recurring title patterns."""
        # Simple pattern matching (can be enhanced with fuzzy matching)
        patterns = Counter()

        for title in titles:
            # Normalize
            normalized = title.lower().strip()

            # Extract first 3 words as pattern
            words = normalized.split()[:3]
            if len(words) >= 2:
                pattern = " ".join(words)
                patterns[pattern] += 1

        # Return patterns that appear 3+ times
        return [
            pattern for pattern, count in patterns.items()
            if count >= 3
        ]
```

### 2. AI Suggestion Engine

```python
# agents/suggestion_engine.py
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
import os
import json
from services.task_analytics import TaskAnalyticsService
from datetime import datetime

class TaskSuggestionEngine:
    """Generate AI-powered task suggestions."""

    def __init__(self, analytics_service: TaskAnalyticsService):
        self.analytics = analytics_service
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def suggest_next_tasks(
        self,
        current_tasks: List[Dict],
        context: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Suggest what tasks to work on next.

        Args:
            current_tasks: List of current incomplete tasks
            context: Additional context (time of day, user mood, etc.)

        Returns:
            List of suggested tasks with reasoning
        """
        # Get user patterns
        completion_patterns = await self.analytics.get_completion_patterns()
        workload = await self.analytics.get_workload_distribution()

        # Build context for AI
        current_time = datetime.utcnow()
        current_hour = current_time.hour

        prompt = f"""You are a productivity assistant helping a user decide what to work on next.

## Current Context
- Time: {current_time.strftime("%A, %B %d, %Y %I:%M %p")}
- User typically most productive at hours: {completion_patterns.get('most_productive_hours', [])}
- Current workload: {workload['total_active']} active tasks
- High priority tasks: {workload['high_priority_incomplete']}
- Overdue tasks: {workload['overdue']}

## Available Tasks
{json.dumps(current_tasks, indent=2)}

## Your Task
Suggest 3-5 tasks the user should work on next. For each suggestion:
1. Task ID and title
2. Why this task now (reasoning)
3. Estimated time needed
4. Priority score (1-10)

Consider:
- Deadlines and due dates
- Task priority and importance
- Time of day (is user typically productive now?)
- Task dependencies
- Quick wins vs deep work

Format your response as JSON:
{{
  "suggestions": [
    {{
      "task_id": 123,
      "title": "Task title",
      "reason": "Why work on this now",
      "estimated_time": "30 minutes",
      "priority_score": 8
    }}
  ]
}}
"""

        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a productivity optimization assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        return result.get("suggestions", [])

    async def suggest_task_breakdown(
        self,
        task: Dict[str, Any]
    ) -> List[str]:
        """
        Suggest how to break down a large task into subtasks.

        Args:
            task: Task to break down

        Returns:
            List of suggested subtasks
        """
        prompt = f"""Break down this task into 3-5 actionable subtasks.

Task: {task['title']}
Description: {task.get('description', 'No description')}
Priority: {task.get('priority', 'medium')}

Provide specific, actionable subtasks that:
- Are smaller and more manageable
- Can be completed independently
- Follow a logical order
- Are concrete and measurable

Format as JSON:
{{
  "subtasks": [
    "First subtask",
    "Second subtask",
    ...
  ]
}}
"""

        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a task breakdown specialist."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        return result.get("subtasks", [])

    async def suggest_related_tasks(
        self,
        task: Dict[str, Any],
        user_patterns: Dict
    ) -> List[str]:
        """
        Suggest related tasks that often accompany this task.

        Args:
            task: Reference task
            user_patterns: User's common task patterns

        Returns:
            List of suggested related tasks
        """
        common_keywords = user_patterns.get("common_keywords", [])
        tag_patterns = user_patterns.get("common_tag_combinations", [])

        prompt = f"""Based on this task, suggest 2-3 related tasks the user might need.

Task: {task['title']}
Tags: {task.get('tags', [])}

User's common task patterns:
- Keywords: {', '.join(common_keywords[:5])}
- Common tag combos: {tag_patterns[:3]}

Suggest tasks that:
- Are related but not duplicates
- Follow user's patterns
- Make sense in the context
- Are actionable

Format as JSON:
{{
  "related_tasks": [
    "Task suggestion 1",
    "Task suggestion 2"
  ]
}}
"""

        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a task suggestion assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        return result.get("related_tasks", [])

    async def suggest_forgotten_task_actions(
        self,
        forgotten_tasks: List[Dict]
    ) -> Dict[str, Any]:
        """
        Suggest what to do about forgotten tasks.

        Returns:
            Dict with suggestions (complete, reschedule, delete, etc.)
        """
        if not forgotten_tasks:
            return {"message": "No forgotten tasks found"}

        prompt = f"""The user has {len(forgotten_tasks)} tasks that haven't been touched in 7+ days:

{json.dumps(forgotten_tasks, indent=2)}

For each task, recommend one of these actions:
- COMPLETE: If it's still relevant and should be done soon
- RESCHEDULE: If it needs a new deadline
- DELEGATE: If someone else should handle it
- DELETE: If it's no longer relevant
- ARCHIVE: If it's done but not marked as complete

Format as JSON:
{{
  "recommendations": [
    {{
      "task_id": 123,
      "title": "Task title",
      "action": "COMPLETE/RESCHEDULE/etc",
      "reason": "Why this action"
    }}
  ],
  "summary": "Overall suggestion for handling these tasks"
}}
"""

        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a task management advisor."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)
```

### 3. Suggestion API Endpoints

```python
# routes/suggestions.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.auth import get_current_user
from services.task_analytics import TaskAnalyticsService
from agents.suggestion_engine import TaskSuggestionEngine
from sqlalchemy import select, and_
from app.models import Todo

router = APIRouter(prefix="/api/suggestions", tags=["suggestions"])


class NextTasksResponse(BaseModel):
    suggestions: List[Dict[str, Any]]
    context: Dict[str, Any]


class TaskBreakdownRequest(BaseModel):
    task_id: int


class TaskBreakdownResponse(BaseModel):
    task: Dict[str, Any]
    subtasks: List[str]


@router.get("/next-tasks", response_model=NextTasksResponse)
async def get_next_task_suggestions(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get AI suggestions for what to work on next.
    """
    # Initialize services
    analytics = TaskAnalyticsService(db, current_user.id)
    suggestion_engine = TaskSuggestionEngine(analytics)

    # Get current incomplete tasks
    query = select(Todo).where(
        and_(
            Todo.user_id == current_user.id,
            Todo.status != "done"
        )
    ).limit(20)

    result = await db.execute(query)
    tasks = result.scalars().all()

    # Convert to dict
    current_tasks = [
        {
            "id": t.id,
            "title": t.title,
            "priority": t.priority,
            "status": t.status,
            "due_date": t.due_date.isoformat() if t.due_date else None,
            "tags": t.tags
        }
        for t in tasks
    ]

    # Get workload context
    workload = await analytics.get_workload_distribution()

    # Get suggestions
    suggestions = await suggestion_engine.suggest_next_tasks(
        current_tasks=current_tasks,
        context={"workload": workload}
    )

    return NextTasksResponse(
        suggestions=suggestions,
        context=workload
    )


@router.post("/breakdown", response_model=TaskBreakdownResponse)
async def get_task_breakdown(
    request: TaskBreakdownRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get AI suggestions for breaking down a task into subtasks.
    """
    # Get task
    task = await db.get(Todo, request.task_id)

    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    # Initialize services
    analytics = TaskAnalyticsService(db, current_user.id)
    suggestion_engine = TaskSuggestionEngine(analytics)

    # Get subtask suggestions
    subtasks = await suggestion_engine.suggest_task_breakdown({
        "title": task.title,
        "description": task.description,
        "priority": task.priority
    })

    return TaskBreakdownResponse(
        task={
            "id": task.id,
            "title": task.title,
            "description": task.description
        },
        subtasks=subtasks
    )


@router.get("/forgotten")
async def get_forgotten_tasks(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get forgotten tasks with AI suggestions on what to do.
    """
    analytics = TaskAnalyticsService(db, current_user.id)
    suggestion_engine = TaskSuggestionEngine(analytics)

    # Get forgotten tasks
    forgotten = await analytics.get_forgotten_tasks()

    if not forgotten:
        return {
            "message": "No forgotten tasks! You're on top of things.",
            "tasks": []
        }

    # Convert to dict
    forgotten_dicts = [
        {
            "id": t.id,
            "title": t.title,
            "created_at": t.created_at.isoformat(),
            "priority": t.priority,
            "status": t.status
        }
        for t in forgotten
    ]

    # Get AI recommendations
    recommendations = await suggestion_engine.suggest_forgotten_task_actions(
        forgotten_dicts
    )

    return {
        "tasks": forgotten_dicts,
        "recommendations": recommendations
    }


@router.get("/patterns")
async def get_user_patterns(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get user's task patterns and productivity insights.
    """
    analytics = TaskAnalyticsService(db, current_user.id)

    completion_patterns = await analytics.get_completion_patterns()
    task_patterns = await analytics.get_common_task_patterns()
    workload = await analytics.get_workload_distribution()

    return {
        "completion_patterns": completion_patterns,
        "task_patterns": task_patterns,
        "workload": workload
    }
```

### 4. Frontend Suggestion Component

```typescript
// components/suggestions/NextTasksSuggestions.tsx
'use client'

import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { Clock, TrendingUp, Lightbulb } from 'lucide-react'

interface TaskSuggestion {
  task_id: number
  title: string
  reason: string
  estimated_time: string
  priority_score: number
}

export function NextTasksSuggestions() {
  const { data, isLoading } = useQuery({
    queryKey: ['next-tasks'],
    queryFn: async () => {
      const res = await fetch('/api/suggestions/next-tasks', {
        credentials: 'include'
      })
      return res.json()
    }
  })

  if (isLoading) {
    return <div className="animate-pulse">Loading suggestions...</div>
  }

  const suggestions: TaskSuggestion[] = data?.suggestions || []

  if (suggestions.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No suggestions available. Complete more tasks to get personalized recommendations!
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-lg font-semibold">
        <Lightbulb className="text-yellow-500" />
        <span>Suggested Next Tasks</span>
      </div>

      {suggestions.map((suggestion, index) => (
        <div
          key={suggestion.task_id}
          className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow"
        >
          {/* Priority Badge */}
          <div className="flex items-start justify-between mb-2">
            <div className="flex items-center gap-2">
              <span className="text-lg font-bold text-blue-600">
                #{index + 1}
              </span>
              <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                {suggestion.title}
              </h3>
            </div>
            <div className="flex items-center gap-1 bg-blue-100 dark:bg-blue-900/30 px-2 py-1 rounded">
              <TrendingUp size={14} className="text-blue-600" />
              <span className="text-sm font-semibold text-blue-600">
                {suggestion.priority_score}/10
              </span>
            </div>
          </div>

          {/* Reason */}
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
            {suggestion.reason}
          </p>

          {/* Time Estimate */}
          <div className="flex items-center gap-1 text-sm text-gray-500">
            <Clock size={14} />
            <span>{suggestion.estimated_time}</span>
          </div>
        </div>
      ))}
    </div>
  )
}
```

---

## Best Practices

### 1. Balance AI Cost vs Value
```python
# ✅ Use cheaper model for simple suggestions
model = "gpt-4o-mini" if simple_suggestion else "gpt-4o"
```

### 2. Cache Suggestions
```python
# ✅ Cache suggestions for 1 hour
@lru_cache(maxsize=100)
async def get_suggestions(user_id: int, cache_key: str):
    ...
```

### 3. Respect User Patterns
```python
# ✅ Use user's productivity patterns
if current_hour in user.most_productive_hours:
    # Suggest deep work tasks
else:
    # Suggest quick tasks
```

### 4. Provide Reasoning
```python
# ✅ Always explain WHY a task is suggested
{
  "task": "Write report",
  "reason": "Due tomorrow and marked high priority"
}
```

---

**Last Updated:** 2026-01-12
**Skill Version:** 1.0.0
**Recommended For:** Phase 3 AI Chatbot - Task Suggestions
