from datetime import date, timedelta
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from library.models import Book, Borrowing, Cover
from user.models import User


BORROWING_URL = "/api/library/borrowings/"


class BorrowingCreationTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="user@test.com",
            password="testpass123"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            inventory=3,
            cover=Cover.HARD,
            daily_fee=1.99
        )

    def test_create_borrowing_decreases_inventory(self):
        self.client.force_authenticate(user=self.user)

        initial_inventory = self.book.inventory
        expected_return = date.today() + timedelta(days=7)

        payload = {
            "book": self.book.id,
            "expected_return_date": expected_return.isoformat()
        }

        response = self.client.post(BORROWING_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, initial_inventory - 1)

    def test_create_borrowing_sets_user_automatically(self):
        self.client.force_authenticate(user=self.user)

        expected_return = date.today() + timedelta(days=14)

        payload = {
            "book": self.book.id,
            "expected_return_date": expected_return.isoformat()
        }

        response = self.client.post(BORROWING_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        borrowing = Borrowing.objects.get(id=response.data["id"])
        self.assertEqual(borrowing.user, self.user)

    def test_cannot_borrow_book_with_zero_inventory(self):
        self.client.force_authenticate(user=self.user)

        self.book.inventory = 0
        self.book.save()

        expected_return = date.today() + timedelta(days=7)

        payload = {
            "book": self.book.id,
            "expected_return_date": expected_return.isoformat()
        }

        response = self.client.post(BORROWING_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "Book not available")

    def test_anonymous_user_cannot_create_borrowing(self):
        expected_return = date.today() + timedelta(days=7)

        payload = {
            "book": self.book.id,
            "expected_return_date": expected_return.isoformat()
        }

        response = self.client.post(BORROWING_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BorrowingReturnTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="user@test.com",
            password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            inventory=2,
            cover=Cover.SOFT,
            daily_fee=3.00
        )
        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=7)
        )
        self.book.inventory = 1
        self.book.save()

    def test_return_book_increases_inventory(self):

        initial_inventory = self.book.inventory

        response = self.client.post(
            f"{BORROWING_URL}{self.borrowing.id}/return_book/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Book returned successfully")

        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, initial_inventory + 1)

    def test_return_book_sets_actual_return_date(self):

        self.assertIsNone(self.borrowing.actual_return_date)

        response = self.client.post(
            f"{BORROWING_URL}{self.borrowing.id}/return_book/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.borrowing.refresh_from_db()
        self.assertIsNotNone(self.borrowing.actual_return_date)

    def test_cannot_return_already_returned_book(self):

        self.borrowing.actual_return_date = timezone.now()
        self.borrowing.save()

        response = self.client.post(
            f"{BORROWING_URL}{self.borrowing.id}/return_book/"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "Already returned")

    def test_return_book_with_get_method(self):

        response = self.client.get(
            f"{BORROWING_URL}{self.borrowing.id}/return_book/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.borrowing.refresh_from_db()
        self.assertIsNotNone(self.borrowing.actual_return_date)


class BorrowingListTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            email="user1@test.com",
            password="testpass123"
        )
        self.client.force_authenticate(user=self.user1)
        self.user2 = User.objects.create_user(
            email="user2@test.com",
            password="testpass123"
        )
        self.book1 = Book.objects.create(
            title="Book 1",
            author="Author 1",
            inventory=5,
            cover=Cover.HARD,
            daily_fee=2.00
        )
        self.book2 = Book.objects.create(
            title="Book 2",
            author="Author 2",
            inventory=3,
            cover=Cover.SOFT,
            daily_fee=1.50
        )

    def test_list_borrowings_shows_book_and_user_details(self):

        borrowing = Borrowing.objects.create(
            user=self.user1,
            book=self.book1,
            expected_return_date=date.today() + timedelta(days=7)
        )

        response = self.client.get(BORROWING_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["book_title"], "Book 1")
        self.assertEqual(response.data["results"][0]["user_email"], "user1@test.com")

    def test_borrowings_ordered_by_expected_return_date(self):

        borrowing1 = Borrowing.objects.create(
            user=self.user1,
            book=self.book1,
            expected_return_date=date.today() + timedelta(days=3)
        )
        borrowing2 = Borrowing.objects.create(
            user=self.user1,
            book=self.book2,
            expected_return_date=date.today() + timedelta(days=10)
        )

        response = self.client.get(BORROWING_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["results"][0]["id"], borrowing2.id)
        self.assertEqual(response.data["results"][1]["id"], borrowing1.id)
