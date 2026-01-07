from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Borrowing, Notification
from .tasks import send_notification

@receiver(post_save, sender=Borrowing)
def borrowing_post_save(sender, instance, created, **kwargs):

    if created:

        notif = Notification.objects.create(
            type="NEW_BORROWING",
            borrowing=instance,
            status="PENDING",
        )

        send_notification.delay(notif.id)
