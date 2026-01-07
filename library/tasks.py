from django.utils import timezone

from library.models import Borrowing, Notification

import requests
from celery import shared_task
from django.conf import settings


TELEGRAM_API_URL = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage"
ADMIN_CHAT_IDS = settings.TELEGRAM_ADMIN_CHAT_IDS


def send_telegram_message(chat_id, text):
    response = requests.post(
        TELEGRAM_API_URL,
        data={"chat_id": chat_id, "text": text},
        timeout=5
    )
    response.raise_for_status()
    return response.json()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_notification(self, notification_id):
    notif = Notification.objects.get(id=notification_id)
    try:
        if notif.type == "NEW_BORROWING" and notif.borrowing:
            text = (
                f"New borrowing: {notif.borrowing.book.title} "
                f"by {notif.borrowing.user.email}, due"
                f" {notif.borrowing.expected_return_date}"
            )
        elif notif.type == "OVERDUE" and notif.borrowing:
            text = (
                f"Overdue borrowing: "
                f"{notif.borrowing.book.title} by "
                f"{notif.borrowing.user.email}, was due "
                f"{notif.borrowing.expected_return_date}"
            )

        else:
            text = "Unknown notification"

        for chat_id in ADMIN_CHAT_IDS:
            send_telegram_message(chat_id, text)

        notif.status = "SENT"
        notif.sent_at = timezone.now()
        notif.save()

    except Exception as exc:
        notif.status = "FAILED"
        notif.error_message = str(exc)
        notif.save()
        raise self.retry(exc=exc)


@shared_task
def check_overdue_borrowings():
    today = timezone.now().date()
    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lt=today, actual_return_date__isnull=True
    )
    for b in overdue_borrowings:
        if not Notification.objects.filter(
            type="OVERDUE", borrowing=b, status="SENT"
        ).exists():
            notif = Notification.objects.create(type="OVERDUE", borrowing=b)
            send_notification.delay(notif.id)
