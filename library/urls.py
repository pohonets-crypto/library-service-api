from django.urls import path, include
from rest_framework import routers

from library.views import BookViewSet, BorrowingViewSet


router = routers.DefaultRouter()
router.register("books", BookViewSet)
router.register("borrowings", BorrowingViewSet)

app_name = "library"

urlpatterns = [
    path("", include(router.urls)),
]
