from django.urls import path
from .views import product_list, auction_list, auction_detail, register, login

urlpatterns = [
    path('api/products/', product_list, name='product_list'),
    path('api/auctions/', auction_list, name='auction_list'),
    path('api/auctions/<int:pk>/', auction_detail, name='auction_detail'),
    path('api/register/', register, name='register'),
    path('api/login/', login, name='login'),
]

