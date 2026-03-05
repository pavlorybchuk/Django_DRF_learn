from django.urls import path
from . import views

urlpatterns = [
    # ── User endpoints ──
    path('users', views.UserCreateView.as_view()),                        # POST
    path('users/users/me/', views.CurrentUserView.as_view()),             # GET

    # ── Categories ──
    path('categories', views.CategoryListView.as_view()),                 # GET, POST

    # ── Menu items ──
    path('menu-items', views.MenuItemListView.as_view()),                 # GET, POST
    path('menu-items/<int:pk>', views.MenuItemDetailView.as_view()),      # GET, PUT, PATCH, DELETE

    # ── Cart ──
    path('cart/menu-items', views.CartMenuItemView.as_view()),            # GET, POST, DELETE

    # ── Orders ──
    path('orders', views.OrderListView.as_view()),                        # GET, POST
    path('orders/<int:orderId>', views.OrderDetailView.as_view()),        # GET, PUT, PATCH, DELETE

    # ── Manager group management ──
    path('groups/manager/users', views.ManagerUserListView.as_view()),            # GET, POST
    path('groups/manager/users/<int:userId>', views.ManagerUserDetailView.as_view()),  # DELETE

    # ── Delivery crew group management ──
    path('groups/delivery-crew/users', views.DeliveryCrewListView.as_view()),          # GET, POST
    path('groups/delivery-crew/users/<int:userId>', views.DeliveryCrewDetailView.as_view()),  # DELETE
]