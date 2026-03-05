from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializers import (
    UserSerializer, CategorySerializer, MenuItemSerializer,
    CartSerializer, OrderSerializer
)
from .permissions import IsManager, IsDeliveryCrew, IsCustomer


# ──────────────────────────────────────────────
# USER REGISTRATION
# ──────────────────────────────────────────────

class UserCreateView(generics.CreateAPIView):
    """POST /api/users — register a new user (no auth required)"""
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        if not username or not password:
            return Response({'error': 'username and password are required'}, status=400)
        user = User.objects.create_user(username=username, email=email, password=password)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class CurrentUserView(APIView):
    """GET /api/users/users/me/ — get current authenticated user"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


# ──────────────────────────────────────────────
# MANAGER GROUP MANAGEMENT
# ──────────────────────────────────────────────

class ManagerUserListView(APIView):
    """GET/POST /api/groups/manager/users"""
    permission_classes = [IsAdminUser | IsManager]

    def get(self, request):
        managers = User.objects.filter(groups__name='Manager')
        return Response(UserSerializer(managers, many=True).data)

    def post(self, request):
        username = request.data.get('username')
        user = get_object_or_404(User, username=username)
        manager_group, _ = Group.objects.get_or_create(name='Manager')
        manager_group.user_set.add(user)
        return Response({'message': f'{username} added to Manager group'}, status=201)


class ManagerUserDetailView(APIView):
    """DELETE /api/groups/manager/users/{userId}"""
    permission_classes = [IsAdminUser | IsManager]

    def delete(self, request, userId):
        user = get_object_or_404(User, id=userId)
        manager_group = get_object_or_404(Group, name='Manager')
        if not manager_group.user_set.filter(id=userId).exists():
            return Response({'error': 'User not found in Manager group'}, status=404)
        manager_group.user_set.remove(user)
        return Response({'message': 'User removed from Manager group'}, status=200)


# ──────────────────────────────────────────────
# DELIVERY CREW GROUP MANAGEMENT
# ──────────────────────────────────────────────

class DeliveryCrewListView(APIView):
    """GET/POST /api/groups/delivery-crew/users"""
    permission_classes = [IsAdminUser | IsManager]

    def get(self, request):
        crew = User.objects.filter(groups__name='Delivery crew')
        return Response(UserSerializer(crew, many=True).data)

    def post(self, request):
        username = request.data.get('username')
        user = get_object_or_404(User, username=username)
        crew_group, _ = Group.objects.get_or_create(name='Delivery crew')
        crew_group.user_set.add(user)
        return Response({'message': f'{username} added to Delivery crew group'}, status=201)


class DeliveryCrewDetailView(APIView):
    """DELETE /api/groups/delivery-crew/users/{userId}"""
    permission_classes = [IsAdminUser | IsManager]

    def delete(self, request, userId):
        user = get_object_or_404(User, id=userId)
        crew_group = get_object_or_404(Group, name='Delivery crew')
        if not crew_group.user_set.filter(id=userId).exists():
            return Response({'error': 'User not found in Delivery crew group'}, status=404)
        crew_group.user_set.remove(user)
        return Response({'message': 'User removed from Delivery crew group'}, status=200)


# ──────────────────────────────────────────────
# MENU ITEMS
# ──────────────────────────────────────────────

class MenuItemListView(generics.ListCreateAPIView):
    """GET/POST /api/menu-items"""
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['category__slug']
    ordering_fields = ['price']
    search_fields = ['title']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAdminUser() | IsManager()]

    def create(self, request, *args, **kwargs):
        if request.user.groups.filter(name__in=['Customer', 'Delivery crew']).exists():
            return Response({'error': 'Unauthorized'}, status=403)
        return super().create(request, *args, **kwargs)


class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/PATCH/DELETE /api/menu-items/{menuItem}"""
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAdminUser() | IsManager()]

    def update(self, request, *args, **kwargs):
        if request.user.groups.filter(name__in=['Customer', 'Delivery crew']).exists():
            return Response({'error': 'Unauthorized'}, status=403)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if request.user.groups.filter(name__in=['Customer', 'Delivery crew']).exists():
            return Response({'error': 'Unauthorized'}, status=403)
        return super().destroy(request, *args, **kwargs)


# ──────────────────────────────────────────────
# CATEGORIES
# ──────────────────────────────────────────────

class CategoryListView(generics.ListCreateAPIView):
    """GET /api/categories — all users; POST — admin/manager"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAdminUser() | IsManager()]


# ──────────────────────────────────────────────
# CART
# ──────────────────────────────────────────────

class CartMenuItemView(APIView):
    """GET/POST/DELETE /api/cart/menu-items"""
    permission_classes = [IsAuthenticated, IsCustomer]

    def get(self, request):
        cart_items = Cart.objects.filter(user=request.user).select_related('menuitem')
        return Response(CartSerializer(cart_items, many=True).data)

    def post(self, request):
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)

    def delete(self, request):
        Cart.objects.filter(user=request.user).delete()
        return Response({'message': 'Cart cleared'}, status=200)


# ──────────────────────────────────────────────
# ORDERS
# ──────────────────────────────────────────────

class OrderListView(APIView):
    """GET/POST /api/orders"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.groups.filter(name='Manager').exists() or user.is_staff:
            orders = Order.objects.all().prefetch_related('items__menuitem')
        elif user.groups.filter(name='Delivery crew').exists():
            orders = Order.objects.filter(delivery_crew=user).prefetch_related('items__menuitem')
        else:
            orders = Order.objects.filter(user=user).prefetch_related('items__menuitem')
        return Response(OrderSerializer(orders, many=True).data)

    def post(self, request):
        # Only customers can place orders
        user = request.user
        cart_items = Cart.objects.filter(user=user).select_related('menuitem')
        if not cart_items.exists():
            return Response({'error': 'Cart is empty'}, status=400)

        total = sum(item.price for item in cart_items)
        order = Order.objects.create(user=user, total=total)

        order_items = [
            OrderItem(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price,
            )
            for item in cart_items
        ]
        OrderItem.objects.bulk_create(order_items)
        cart_items.delete()

        return Response(OrderSerializer(order).data, status=201)


class OrderDetailView(APIView):
    """GET/PUT/PATCH/DELETE /api/orders/{orderId}"""
    permission_classes = [IsAuthenticated]

    def get_order(self, orderId):
        return get_object_or_404(Order, id=orderId)

    def get(self, request, orderId):
        order = self.get_order(orderId)
        user = request.user
        if not (user.is_staff or user.groups.filter(name='Manager').exists()):
            if order.user != user:
                return Response({'error': 'Forbidden'}, status=403)
        return Response(OrderSerializer(order).data)

    def put(self, request, orderId):
        return self._update(request, orderId, partial=False)

    def patch(self, request, orderId):
        return self._update(request, orderId, partial=True)

    def _update(self, request, orderId, partial):
        order = self.get_order(orderId)
        user = request.user

        # Delivery crew can only update status
        if user.groups.filter(name='Delivery crew').exists():
            if order.delivery_crew != user:
                return Response({'error': 'Forbidden'}, status=403)
            new_status = request.data.get('status')
            if new_status is not None:
                order.status = bool(int(new_status))
                order.save()
            return Response(OrderSerializer(order).data)

        # Manager can assign delivery crew and update status
        if user.groups.filter(name='Manager').exists() or user.is_staff:
            delivery_crew_id = request.data.get('delivery_crew')
            new_status = request.data.get('status')
            if delivery_crew_id:
                crew = get_object_or_404(User, id=delivery_crew_id)
                order.delivery_crew = crew
            if new_status is not None:
                order.status = bool(int(new_status))
            order.save()
            return Response(OrderSerializer(order).data)

        return Response({'error': 'Unauthorized'}, status=403)

    def delete(self, request, orderId):
        user = request.user
        if not (user.is_staff or user.groups.filter(name='Manager').exists()):
            return Response({'error': 'Unauthorized'}, status=403)
        order = self.get_order(orderId)
        order.delete()
        return Response({'message': 'Order deleted'}, status=200)