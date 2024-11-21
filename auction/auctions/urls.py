from django.urls import path
from .views import product_list, auction_list, auction_detail, register, login, profile, update_profile, rate_user, \
    create_auction, create_product, get_categories, refresh_token

urlpatterns = [
    path('api/products/', product_list, name='product_list'),
    path('api/create-product/', create_product, name='create_product'),
    path('api/auctions/', auction_list, name='auction_list'),
    path('api/auction/<int:pk>/', auction_detail, name='auction_detail'),
    path('api/create-auction/', create_auction, name='create_auction'),
    path('api/register/', register, name='register'),
    path('api/login/', login, name='login'),
    path('api/profile/', profile, name='profile'),
    path('api/users/<int:user_id>/rate/', rate_user, name='rate_user'),
    path('api/profile/update/', update_profile, name='update_profile'),
    path('api/categories/', get_categories, name='get_categories'),
    path('api/token/refresh/', refresh_token, name='refresh_token')
]

