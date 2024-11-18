from django.urls import path
from .views import product_list, auction_list, auction_detail, register, login, profile, update_profile, rate_user

urlpatterns = [
    path('api/products/', product_list, name='product_list'),
    path('api/auctions/', auction_list, name='auction_list'),
    path('api/auctions/<int:pk>/', auction_detail, name='auction_detail'),
    path('api/register/', register, name='register'),
    path('api/login/', login, name='login'),
    path('api/profile/', profile, name='profile'),
    path('api/users/<int:user_id>/rate/', rate_user, name='rate_user'),
    path('api/profile/update/', update_profile, name='update_profile'),
]

