from rest_framework import serializers

from library.models import Book, Borrowing


class BookListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "author",
        )
        read_only_fields = ("id",)


class BookDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "author",
            "inventory",
            "cover",
            "daily_fee"
        )
        read_only_fields = (
            "id",

        )


class BorrowingListSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(
        source="book.title", read_only=True)
    user_email = serializers.CharField(
        source="user.email", read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book_title",
            "borrow_date",
            "actual_return_date",
            "user_email"
        )
        read_only_fields = ("id", "borrow_date")


class BorrowingDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "user"
        )
        read_only_fields = ("id", "borrow_date")