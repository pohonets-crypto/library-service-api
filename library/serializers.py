from rest_framework import serializers

from library.models import Book


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
        read_only_fields = ("id",)