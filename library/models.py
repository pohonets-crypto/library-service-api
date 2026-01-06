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
    cover = models.CharField(
        max_length=4,
        choices = Cover.choices,
        default=Cover.SOFT)
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

    def __str__(self):
        return f"{self.book} borrowing {self.expected_return_date}"


class Status(models.TextChoices):
    PENDING = "PENDING", "Pending"
    PAID = "PAID", "Paid"

class Type(models.TextChoices):
    PAYMENT = "PAYMENT", "Payment"
    FINE = "FINE", "Fine"


class Payment(models.Model):
    payment_date = models.DateField(auto_now_add=True)
    status = models.CharField(
        choices=Status.choices,
        default=Status.PENDING,
        max_length=7,
    )
    type = models.CharField(
        choices=Type.choices,
        default=Type.PAYMENT,
        max_length=7,
    )
    borrowing = models.ForeignKey(
        Borrowing, on_delete=models.CASCADE)
    session_url = models.URLField(blank=True, null=True)
    session_id = models.CharField(
        max_length=255, blank=True, unique=True, null=True)
    money_to_pay = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Price in USD",
    )

    def __str__(self):
        return f"{self.type} payment {self.payment_date}"
