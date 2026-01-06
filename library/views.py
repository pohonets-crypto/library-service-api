from django.shortcuts import render
from rest_framework import mixins, viewsets
from rest_framework.viewsets import GenericViewSet

from library.models import Book
from library.serializers import BookListSerializer, BookDetailSerializer


# Create your views here.
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer
        return BookDetailSerializer
