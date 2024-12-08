from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import product_list, auction_list, auction_detail, register, login, profile, update_profile, rate_user, \
    create_auction, create_product, get_categories, refresh_token, user_profile_view, update_auction, update_product, \
    current_user, product_detail, add_to_favorites, remove_from_favorites, is_favorite, auction_status, place_bid, \
    change_user_role, stats_view

urlpatterns = [
    path('api/products/', product_list, name='product_list'),
    path('api/create-product/', create_product, name='create_product'),
    path('api/product/<int:pk>/update/', update_product, name='update_product'),
    path('api/product/<int:pk>/', product_detail, name='product_detail'),
    path('api/auctions/', auction_list, name='auction_list'),
    path('api/auction/<int:pk>/', auction_detail, name='auction_detail'),
    path('api/auction/<int:pk>/update/', update_auction, name='update_auction'),
    path('api/create-auction/', create_auction, name='create_auction'),
    path('api/auction/<int:pk>/favorite/', add_to_favorites, name='add_to_favorites'),
    path('api/auction/<int:pk>/favorite/remove/', remove_from_favorites, name='remove_from_favorites'),
    path('api/auction/<int:pk>/is_favorite/', is_favorite, name='is_favorite'),
    path('api/auction/<int:pk>/bid/', place_bid, name='place_bid'),
    path('api/auction/status/', auction_status, name='auction_status'),
    path('api/users/change-role/', change_user_role, name='change_role'),
    path('api/register/', register, name='register'),
    path('api/login/', login, name='login'),
    path('api/current_user/', current_user, name='current_user'),
    path('api/profile/', profile, name='profile'),
    path('api/users/<int:user_id>/profile/', user_profile_view, name='profile'),
    path('api/users/<int:user_id>/rate/', rate_user, name='rate_user'),
    path('api/profile/update/', update_profile, name='update_profile'),
    path('api/categories/', get_categories, name='get_categories'),
    path('api/token/refresh/', refresh_token, name='refresh_token'),
    path('api/stats/', stats_view, name='stats-api'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
