import json
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics
from .serializers import BookSerializer
from .models import Book
from django.views.decorators.http import require_http_methods
from decimal import Decimal, InvalidOperation
from .permissions import IsBookManagerOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


def validate_title_author(data):
    if "title" in data and not str(data["title"]).strip():
        return "Field 'title' cannot be empty."
    if "author" in data and not str(data["author"]).strip():
        return "Field 'author' cannot be empty."
    return None


def parse_and_validate_price_inventory(data):
    price = None
    inventory = None

    if "price" in data:
        try:
            price = Decimal(str(data["price"]))
        except (InvalidOperation, TypeError):
            return None, None, "Field 'price' must be a valid decimal."
        if price < 0:
            return None, None, "Field 'price' must be >= 0."

    if "inventory" in data:
        try:
            inventory = int(data["inventory"])
        except (TypeError, ValueError):
            return None, None, "Field 'inventory' must be an integer."
        if inventory < 0:
            return None, None, "Field 'inventory' must be >= 0."

    return price, inventory, None


def book_to_dict(book: Book):
    return {
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "price": str(book.price),
        "inventory": book.inventory,
    }


def read_json_body(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON")


@csrf_exempt
@require_http_methods(["GET", "POST"])
def books_v1(request):
    if request.method == "GET":
        books = Book.objects.all().order_by("id")
        return JsonResponse([book_to_dict(b) for b in books], safe=False)
    else:
        try:
            data = read_json_body(request)
        except ValueError as e:
            return JsonResponse({"detail": str(e)}, status=400)

        required = ["title", "author", "price", "inventory"]
        missing = [k for k in required if k not in data]
        if missing:
            return JsonResponse(
                {"detail": f"Missing fields: {', '.join(missing)}"}, status=400
            )

        err = validate_title_author(data)
        if err:
            return JsonResponse({"detail": err}, status=400)

        _, _, err = parse_and_validate_price_inventory(data)
        if err:
            return JsonResponse({"detail": err}, status=400)

        try:
            book = Book.objects.create(
                title=str(data["title"]),
                author=str(data["author"]),
                price=Decimal(str(data["price"])),
                inventory=int(data["inventory"]),
            )
        except Exception as e:
            return JsonResponse({"detail": f"Invalid data: {e}"}, status=400)

        return JsonResponse(book_to_dict(book), status=201)


@csrf_exempt
@require_http_methods(["GET", "DELETE", "PATCH"])
def book_detail_v1(request, book_id):
    try:
        book = Book.objects.get(pk=book_id)
    except Book.DoesNotExist:
        return JsonResponse({"detail": "Not found"}, status=404)

    if request.method == "GET":
        return JsonResponse(book_to_dict(book))

    if request.method == "DELETE":
        book.delete()
        return JsonResponse({"detail": "Deleted"}, status=204)

    else:
        try:
            data = read_json_body(request)
        except ValueError as e:
            return JsonResponse({"detail": str(e)}, status=400)

        allowed = {"title", "author", "price", "inventory"}
        unknown = [k for k in data.keys() if k not in allowed]
        if unknown:
            return JsonResponse(
                {"detail": f"Unknown fields: {', '.join(unknown)}"}, status=400
            )

        err = validate_title_author(data)
        if err:
            return JsonResponse({"detail": err}, status=400)

        price, inventory, err = parse_and_validate_price_inventory(data)
        if err:
            return JsonResponse({"detail": err}, status=400)

        if "title" in data:
            book.title = str(data["title"]).strip()
        if "author" in data:
            book.author = str(data["author"]).strip()
        if "price" in data:
            book.price = price
        if "inventory" in data:
            book.inventory = inventory

        book.save()
        return JsonResponse(book_to_dict(book))


class BookListCreateV2(generics.ListCreateAPIView):
    queryset = Book.objects.all().order_by("id")
    serializer_class = BookSerializer
    permission_classes = [IsBookManagerOrReadOnly]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]


class BookDetailV2(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    http_method_names = ["get", "patch", "delete"]
    permission_classes = [IsBookManagerOrReadOnly]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]


class LogoutAndBlacklistRefreshTokenView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            return Response(
                {"detail": "refresh is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh)
            token.blacklist()
        except Exception:
            return Response(
                {"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"detail": "Logged out"}, status=status.HTTP_205_RESET_CONTENT)
