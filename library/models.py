from django.core.validators import MinValueValidator
from django.db import models

from user.models import User


class Cover(models.TextChoices):
    HARD = "HARD", "Hard"
    SOFT = "SOFT", "Soft"


class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    inventory = models.IntegerField(
        validators=[MinValueValidator(0)],
    )
    cover = models.CharField(max_length=4, choices=Cover.choices, default=Cover.SOFT)
    daily_fee = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Price in USD",
    )

    def __str__(self):
        return f"{self.title} by {self.author}"


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrowing")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="borrowing")

    class Meta:
        ordering = ("-expected_return_date",)

    def __str__(self):
        return f"{self.book} borrowing {self.expected_return_date}"


class Notification(models.Model):
    NOTIF_TYPES = [
        ("NEW_BORROWING", "New Borrowing"),
        ("OVERDUE", "Overdue"),
    ]

    type = models.CharField(max_length=20, choices=NOTIF_TYPES)
    borrowing = models.ForeignKey(
        Borrowing, on_delete=models.CASCADE, null=True, blank=True
    )
    payment_id = models.IntegerField(null=True, blank=True)
    status = models.CharField(
        max_length=10,
        choices=[("PENDING", "Pending"), ("SENT", "Sent")],
        default="PENDING",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
