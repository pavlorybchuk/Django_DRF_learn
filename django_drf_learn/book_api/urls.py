from django.urls import path
from .views import books_v1, book_detail_v1, BookDetailV2, BookListCreateV2

urlpatterns = [
    path("v1/books", books_v1, name="books_v1"),
    path("v1/books/<int:book_id>", book_detail_v1, name="book_detail_v1"),
    path("v2/books", BookListCreateV2.as_view(), name="books_v2"),
    path("v2/books/<int:pk>", BookDetailV2.as_view(), name="book_detail_v2"),
]
