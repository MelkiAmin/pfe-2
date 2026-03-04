from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_ticket_confirmation_email(user_email, event_title, ticket_number):
    send_mail(
        subject=f'Ticket Confirmed – {event_title}',
        message=f'Your ticket #{ticket_number} for "{event_title}" has been confirmed.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )


@shared_task
def send_event_reminder_email(user_email, event_title, start_date):
    send_mail(
        subject=f'Reminder: {event_title} is tomorrow!',
        message=f'Don\'t forget! "{event_title}" starts on {start_date}.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )


@shared_task
def send_event_cancellation_email(user_email, event_title):
    send_mail(
        subject=f'Event Cancelled – {event_title}',
        message=f'"{event_title}" has been cancelled. A refund will be processed shortly.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )


def create_notification(recipient, notification_type, title, message, data=None):
    from .models import Notification
    return Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        title=title,
        message=message,
        data=data or {},
    )