"""Background task scheduler for notifications and reminders."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import async_session_maker
from src.models import Task, User, UserPreferences
from src.services.email_service import email_service

logger = logging.getLogger(__name__)


class SchedulerService:
    """Background scheduler for notifications and automated tasks."""

    def __init__(self):
        self.scheduler: Optional[AsyncIOScheduler] = None
        self._running = False

    async def start(self):
        """Start the background scheduler."""
        if self._running:
            logger.warning("Scheduler already running")
            return

        self.scheduler = AsyncIOScheduler()

        # Add jobs
        # Check for due reminders every 15 minutes
        self.scheduler.add_job(
            self.check_reminders,
            IntervalTrigger(minutes=15),
            id="check_reminders",
            replace_existing=True,
        )

        # Check for overdue tasks every hour
        self.scheduler.add_job(
            self.check_overdue_tasks,
            IntervalTrigger(hours=1),
            id="check_overdue",
            replace_existing=True,
        )

        # Send daily digests (we'll run this every minute and check user preferences)
        self.scheduler.add_job(
            self.send_daily_digests,
            IntervalTrigger(minutes=1),
            id="daily_digests",
            replace_existing=True,
        )

        self.scheduler.start()
        self._running = True
        logger.info("Scheduler started")

    async def stop(self):
        """Stop the background scheduler."""
        if self.scheduler:
            self.scheduler.shutdown(wait=False)
            self._running = False
            logger.info("Scheduler stopped")

    async def check_reminders(self):
        """Check for tasks with reminders due soon and send notifications."""
        logger.debug("Checking reminders...")

        try:
            async with async_session_maker() as session:
                # Find tasks with reminders in the next 15 minutes
                now = datetime.utcnow()
                reminder_window = now + timedelta(minutes=15)

                query = select(Task).where(
                    Task.reminder_at.isnot(None),
                    Task.reminder_at <= reminder_window,
                    Task.reminder_at > now - timedelta(minutes=15),  # Not already sent
                    Task.completed == False,  # noqa: E712
                )

                result = await session.execute(query)
                tasks = result.scalars().all()

                for task in tasks:
                    await self._send_reminder(session, task)

        except Exception as e:
            logger.error(f"Error checking reminders: {e}")

    async def check_overdue_tasks(self):
        """Check for newly overdue tasks and send notifications."""
        logger.debug("Checking overdue tasks...")

        try:
            async with async_session_maker() as session:
                now = datetime.utcnow()
                # Find tasks that became overdue in the last hour
                overdue_window = now - timedelta(hours=1)

                query = select(Task).where(
                    Task.due_date.isnot(None),
                    Task.due_date <= now,
                    Task.due_date > overdue_window,
                    Task.completed == False,  # noqa: E712
                )

                result = await session.execute(query)
                tasks = result.scalars().all()

                for task in tasks:
                    await self._send_overdue_notification(session, task)

        except Exception as e:
            logger.error(f"Error checking overdue tasks: {e}")

    async def send_daily_digests(self):
        """Send daily digest emails to users who have it enabled."""
        logger.debug("Checking daily digests...")

        try:
            async with async_session_maker() as session:
                now = datetime.utcnow()
                current_minute = now.strftime("%H:%M")

                # Find users with daily digest enabled at current time
                query = select(UserPreferences).where(
                    UserPreferences.email_daily_digest == True,  # noqa: E712
                    UserPreferences.reminder_time == current_minute,
                )

                result = await session.execute(query)
                preferences = result.scalars().all()

                for prefs in preferences:
                    await self._send_digest(session, prefs.user_id)

        except Exception as e:
            logger.error(f"Error sending daily digests: {e}")

    async def _send_reminder(self, session: AsyncSession, task: Task):
        """Send a reminder notification for a task."""
        # Get user and preferences
        user = await session.get(User, task.user_id)
        if not user:
            return

        prefs_result = await session.execute(
            select(UserPreferences).where(UserPreferences.user_id == task.user_id)
        )
        prefs = prefs_result.scalar_one_or_none()

        if prefs and not prefs.email_reminders:
            return

        # Send email reminder
        task_url = f"https://todoapp.example.com/tasks/{task.id}"  # Configure from env
        await email_service.send_task_reminder(
            to_email=user.email,
            task_title=task.title,
            due_date=task.due_date,
            task_url=task_url,
        )

        logger.info(f"Sent reminder for task {task.id} to {user.email}")

    async def _send_overdue_notification(self, session: AsyncSession, task: Task):
        """Send an overdue notification for a task."""
        user = await session.get(User, task.user_id)
        if not user:
            return

        prefs_result = await session.execute(
            select(UserPreferences).where(UserPreferences.user_id == task.user_id)
        )
        prefs = prefs_result.scalar_one_or_none()

        if prefs and not prefs.email_reminders:
            return

        task_url = f"https://todoapp.example.com/tasks/{task.id}"
        await email_service.send_overdue_notification(
            to_email=user.email,
            task_title=task.title,
            due_date=task.due_date,
            task_url=task_url,
        )

        logger.info(f"Sent overdue notification for task {task.id} to {user.email}")

    async def _send_digest(self, session: AsyncSession, user_id):
        """Send daily digest to a user."""
        user = await session.get(User, user_id)
        if not user:
            return

        now = datetime.utcnow()
        today_start = datetime(now.year, now.month, now.day)
        today_end = today_start + timedelta(days=1)

        # Get tasks due today
        today_query = select(Task).where(
            Task.user_id == user_id,
            Task.due_date >= today_start,
            Task.due_date < today_end,
            Task.completed == False,  # noqa: E712
        )
        today_result = await session.execute(today_query)
        today_tasks = today_result.scalars().all()

        # Get overdue tasks
        overdue_query = select(Task).where(
            Task.user_id == user_id,
            Task.due_date < today_start,
            Task.completed == False,  # noqa: E712
        )
        overdue_result = await session.execute(overdue_query)
        overdue_tasks = overdue_result.scalars().all()

        if not today_tasks and not overdue_tasks:
            logger.debug(f"No tasks for digest for user {user_id}")
            return

        dashboard_url = "https://todoapp.example.com/dashboard"
        await email_service.send_daily_digest(
            to_email=user.email,
            user_name=user.name,
            tasks_due_today=[
                {
                    "title": t.title,
                    "priority": t.priority,
                    "due_time": t.due_date.strftime("%I:%M %p") if t.due_date else None,
                }
                for t in today_tasks
            ],
            overdue_tasks=[
                {
                    "title": t.title,
                    "priority": t.priority,
                    "due_date": t.due_date.strftime("%b %d") if t.due_date else None,
                }
                for t in overdue_tasks
            ],
            dashboard_url=dashboard_url,
        )

        logger.info(f"Sent daily digest to {user.email}")


# Singleton instance
scheduler_service = SchedulerService()
