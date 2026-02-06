"""Email service for sending notifications."""

import os
from datetime import datetime
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

# Check if SendGrid is available
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content

    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False


class EmailService:
    """Service for sending email notifications using SendGrid."""

    def __init__(self):
        self.api_key = os.environ.get("SENDGRID_API_KEY")
        self.from_email = os.environ.get("SENDGRID_FROM_EMAIL", "noreply@todoapp.com")
        self.from_name = os.environ.get("SENDGRID_FROM_NAME", "TodoX App")
        self.enabled = bool(self.api_key) and SENDGRID_AVAILABLE

        # Setup Jinja2 templates
        template_dir = os.path.join(os.path.dirname(__file__), "..", "templates", "email")
        if os.path.exists(template_dir):
            self.jinja_env = Environment(
                loader=FileSystemLoader(template_dir),
                autoescape=select_autoescape(["html", "xml"]),
            )
        else:
            self.jinja_env = None

    def _render_template(self, template_name: str, **context: Any) -> str:
        """Render an email template with context."""
        if not self.jinja_env:
            # Fallback to basic string formatting
            return self._get_fallback_template(template_name, **context)

        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**context)
        except Exception:
            return self._get_fallback_template(template_name, **context)

    def _get_fallback_template(self, template_name: str, **context: Any) -> str:
        """Get fallback template when Jinja2 templates not available."""
        if "reminder" in template_name:
            return f"""
            <h2>Task Reminder</h2>
            <p>Don't forget about your task: <strong>{context.get('task_title', 'Task')}</strong></p>
            <p>Due: {context.get('due_date', 'Soon')}</p>
            <p><a href="{context.get('task_url', '#')}">View Task</a></p>
            """
        elif "digest" in template_name:
            return f"""
            <h2>Your Daily Task Digest</h2>
            <p>You have {context.get('task_count', 0)} tasks due today.</p>
            <p>Overdue: {context.get('overdue_count', 0)}</p>
            <p><a href="{context.get('dashboard_url', '#')}">View Dashboard</a></p>
            """
        elif "overdue" in template_name:
            return f"""
            <h2>Overdue Task Alert</h2>
            <p>Your task <strong>{context.get('task_title', 'Task')}</strong> is now overdue.</p>
            <p>Was due: {context.get('due_date', 'Past')}</p>
            <p><a href="{context.get('task_url', '#')}">View Task</a></p>
            """
        return "<p>Notification from TodoX App</p>"

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_content: str | None = None,
    ) -> bool:
        """Send an email using SendGrid.

        Returns True if sent successfully, False otherwise.
        """
        if not self.enabled:
            print(f"Email service disabled. Would send to {to_email}: {subject}")
            return False

        try:
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content),
            )

            if plain_content:
                message.add_content(Content("text/plain", plain_content))

            sg = SendGridAPIClient(self.api_key)
            response = sg.send(message)

            return response.status_code in (200, 202)

        except Exception as e:
            print(f"Failed to send email to {to_email}: {e}")
            return False

    async def send_task_reminder(
        self,
        to_email: str,
        task_title: str,
        due_date: datetime,
        task_url: str,
    ) -> bool:
        """Send a task reminder email."""
        html_content = self._render_template(
            "reminder.html",
            task_title=task_title,
            due_date=due_date.strftime("%B %d, %Y at %I:%M %p"),
            task_url=task_url,
        )

        return await self.send_email(
            to_email=to_email,
            subject=f"Reminder: {task_title}",
            html_content=html_content,
        )

    async def send_daily_digest(
        self,
        to_email: str,
        user_name: str,
        tasks_due_today: list[dict],
        overdue_tasks: list[dict],
        dashboard_url: str,
    ) -> bool:
        """Send daily task digest email."""
        html_content = self._render_template(
            "digest.html",
            user_name=user_name or "there",
            tasks_due_today=tasks_due_today,
            task_count=len(tasks_due_today),
            overdue_tasks=overdue_tasks,
            overdue_count=len(overdue_tasks),
            dashboard_url=dashboard_url,
            date=datetime.utcnow().strftime("%B %d, %Y"),
        )

        return await self.send_email(
            to_email=to_email,
            subject=f"Your Daily Task Digest - {len(tasks_due_today)} tasks for today",
            html_content=html_content,
        )

    async def send_overdue_notification(
        self,
        to_email: str,
        task_title: str,
        due_date: datetime,
        task_url: str,
    ) -> bool:
        """Send overdue task notification email."""
        html_content = self._render_template(
            "overdue.html",
            task_title=task_title,
            due_date=due_date.strftime("%B %d, %Y at %I:%M %p"),
            task_url=task_url,
        )

        return await self.send_email(
            to_email=to_email,
            subject=f"Overdue: {task_title}",
            html_content=html_content,
        )


# Singleton instance
email_service = EmailService()
