Migrate and create superuser before use.

**URLS**

GET     /book-api/v1/books #
POST    /book-api/v1/books #
GET     /book-api/v1/books/<id> #
PATCH   /book-api/v1/books/<id> #
DELETE  /book-api/v1/books/<id> #

GET     /book-api/v2/books #
POST    /book-api/v2/books #
GET     /book-api/v2/books/<id> #
PATCH   /book-api/v2/books/<id> #
DELETE  /book-api/v2/books/<id> #

POST    /auth/token/login/ #
POST    /auth/token/logout/ #

POST    /auth/jwt/create/ #
POST    /auth/jwt/refresh/ #
POST    /auth/jwt/verify/ #
POST    /book-api/jwt/logout/ #

POST    /auth/users/ #            
GET     /auth/users/me/ #     
GET     /auth/users/ #            
DELETE  /auth/users/me/ #

/admin/

# Cafe API — Endpoints

Base URL: `/api/`  
Authentication: Token `Authorization: Token <your_token>`

---

## Auth

| Endpoint | Method | Role | Description |
|---|---|---|---|
| `/api/users` | POST | Public | Register a new user |
| `/api/users/users/me/` | GET | Any authenticated | Get current user info |
| `/token/login/` | POST | Public | Get access token (username + password) |
| `/token/logout/` | POST | Any authenticated | Revoke token |

---

## Categories

| Endpoint | Method | Role | Description |
|---|---|---|---|
| `/api/categories` | GET | Any authenticated | List all categories |
| `/api/categories` | POST | Admin, Manager | Create a new category |

---

## Menu Items

| Endpoint | Method | Role | Description |
|---|---|---|---|
| `/api/menu-items` | GET | Any authenticated | List all menu items (supports filtering, sorting, pagination) |
| `/api/menu-items` | POST | Admin, Manager | Create a new menu item → 201 Created |
| `/api/menu-items` | POST, PUT, PATCH, DELETE | Customer, Delivery crew | → 403 Unauthorized |
| `/api/menu-items/{menuItemId}` | GET | Any authenticated | Get a single menu item |
| `/api/menu-items/{menuItemId}` | PUT, PATCH | Admin, Manager | Update a menu item |
| `/api/menu-items/{menuItemId}` | DELETE | Admin, Manager | Delete a menu item |
| `/api/menu-items/{menuItemId}` | POST, PUT, PATCH, DELETE | Customer, Delivery crew | → 403 Unauthorized |

### Query parameters for `/api/menu-items`
| Parameter | Example | Description |
|---|---|---|
| `category__slug` | `?category__slug=burgers` | Filter by category |
| `ordering` | `?ordering=price` or `?ordering=-price` | Sort by price asc/desc |
| `search` | `?search=pizza` | Search by title |
| `page` | `?page=2` | Pagination (10 items per page) |

---

## Cart

| Endpoint | Method | Role | Description |
|---|---|---|---|
| `/api/cart/menu-items` | GET | Customer | List cart items for the current user |
| `/api/cart/menu-items` | POST | Customer | Add a menu item to the cart |
| `/api/cart/menu-items` | DELETE | Customer | Clear all items from the cart |

---

## Orders

| Endpoint | Method | Role | Description |
|---|---|---|---|
| `/api/orders` | GET | Customer | List own orders |
| `/api/orders` | GET | Manager | List all orders from all users |
| `/api/orders` | GET | Delivery crew | List orders assigned to this crew member |
| `/api/orders` | POST | Customer | Place an order (from cart items, then clears cart) |
| `/api/orders/{orderId}` | GET | Customer | Get own order by ID → 403 if not owner |
| `/api/orders/{orderId}` | GET | Manager | Get any order by ID |
| `/api/orders/{orderId}` | PUT, PATCH | Manager | Assign delivery crew, update status (0=out for delivery, 1=delivered) |
| `/api/orders/{orderId}` | PATCH | Delivery crew | Update order status only (0 or 1) |
| `/api/orders/{orderId}` | DELETE | Manager | Delete an order |

---

## Manager Group Management

| Endpoint | Method | Role | Description |
|---|---|---|---|
| `/api/groups/manager/users` | GET | Admin, Manager | List all managers |
| `/api/groups/manager/users` | POST | Admin, Manager | Add user to Manager group → 201 Created |
| `/api/groups/manager/users/{userId}` | DELETE | Admin, Manager | Remove user from Manager group → 200 OK / 404 Not found |

---

## Delivery Crew Group Management

| Endpoint | Method | Role | Description |
|---|---|---|---|
| `/api/groups/delivery-crew/users` | GET | Admin, Manager | List all delivery crew members |
| `/api/groups/delivery-crew/users` | POST | Admin, Manager | Add user to Delivery crew group → 201 Created |
| `/api/groups/delivery-crew/users/{userId}` | DELETE | Admin, Manager | Remove user from Delivery crew group → 200 OK / 404 Not found |