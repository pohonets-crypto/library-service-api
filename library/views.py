from django.utils import timezone
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response

from library.models import Book, Borrowing
from library.serializers import (
    BookListSerializer,
    BookDetailSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
)


# Create your views here.
class BookViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Book.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer
        return BookDetailSerializer


class BorrowingViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):

    queryset = Borrowing.objects.all().select_related()
    permission_classes = [IsAuthenticated, ]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        return BorrowingDetailSerializer

    def create(self, request, *args, **kwargs):
        book_id = request.data.get("book")
        book = Book.objects.get(id=book_id)

        if book.inventory <= 0:
            return Response(
                {"error": "Book not available"}, status=status.HTTP_400_BAD_REQUEST
            )

        book.inventory -= 1
        book.save()

        borrowing = Borrowing.objects.create(
            user=request.user,
            book=book,
            expected_return_date=request.data.get("expected_return_date"),
        )
        return Response(
            {"id": borrowing.id, "message": "Borrowing created"},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get", "post"])
    def return_book(self, request, pk=None):
        borrowing = self.get_object()
        if borrowing.actual_return_date:
            return Response(
                {"error": "Already returned"}, status=status.HTTP_400_BAD_REQUEST
            )

        borrowing.actual_return_date = timezone.now()
        borrowing.save()

        book = borrowing.book
        book.inventory += 1
        book.save()

        return Response({"message": "Book returned successfully"})
