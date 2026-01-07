from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from library.models import Book, Cover
from user.models import User


BOOK_URL = "/api/library/books/"


class BookTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="user@test.com",
            password="testpass123"
        )
        self.admin_user = User.objects.create_user(
            email="admin@test.com",
            password="adminpass123",
            is_staff=True
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            inventory=5,
            cover=Cover.SOFT,
            daily_fee=2.50
        )

    def test_list_books_authenticated(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(BOOK_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Test Book")

    def test_list_books_unauthenticated(self):
        response = self.client.get(BOOK_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_book_detail_authenticated(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f"{BOOK_URL}{self.book.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Book")
        self.assertEqual(response.data["inventory"], 5)
        self.assertEqual(float(response.data["daily_fee"]), 2.50)

    def test_retrieve_book_detail_unauthenticated(self):
        response = self.client.get(f"{BOOK_URL}{self.book.id}/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_book_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)

        payload = {
            "title": "New Book",
            "author": "New Author",
            "inventory": 10,
            "cover": Cover.HARD,
            "daily_fee": 3.00
        }

        response = self.client.post(BOOK_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)
        self.assertEqual(Book.objects.get(id=response.data["id"]).title, "New Book")

    def test_create_book_as_regular_user_forbidden(self):
        self.client.force_authenticate(user=self.user)

        payload = {
            "title": "New Book",
            "author": "New Author",
            "inventory": 10,
            "cover": Cover.HARD,
            "daily_fee": 3.00
        }

        response = self.client.post(BOOK_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
