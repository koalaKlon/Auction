import datetime
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now


class User(AbstractUser):
    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('user', 'User'),
        ('manager', 'Manager')
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    profile_picture = models.ImageField(upload_to='user_profiles/', blank=True, null=True)
    email = models.EmailField(unique=True)  # Добавление поля email

    def calculate_average_rating(self):
        """Пересчитываем средний рейтинг пользователя."""
        ratings = Rating.objects.filter(user=self)  # Получаем все рейтинги для данного пользователя
        if ratings:
            total_rating = sum([rating.rating for rating in ratings])
            avg_rating = total_rating / len(ratings)
            self.rating = avg_rating  # Обновляем рейтинг
            self.save()
        else:
            self.rating = 0  # Если нет рейтингов, ставим 0
            self.save()

    # Уникальные и осмысленные имена для связанных полей
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='users_in_group',  # Лучше выбрать осмысленное имя
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='permissions_for_user',  # Осмысленное имя
        blank=True
    )

    def __str__(self):
        return self.username


class Rating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='given_ratings')
    rated_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_ratings', null=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Rating {self.rating} for {self.rated_user} by {self.user}'


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                   related_name='created_categories')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products')
    starting_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Auction(models.Model):
    AUCTION_TYPE_CHOICES = [
        ('single', 'Single Product Auction'),
        ('multiple', 'Multiple Products Auction'),
    ]
    auction_type = models.CharField(max_length=20, choices=AUCTION_TYPE_CHOICES, default='single')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    products = models.ManyToManyField(Product, blank=True, related_name='auctions')
    current_bid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_favorite = models.BooleanField(default=False)
    start_time = models.DateTimeField(default=now)
    end_time = models.DateTimeField(default=now() + datetime.timedelta(days=7))
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='seller_auctions')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='buyer_auctions')
    banner_image = models.ImageField(upload_to='auction_banners/', blank=True, null=True)
    status = models.CharField(max_length=20, default='planned')

    def update_status(self):
        now = datetime.timezone.now()
        if self.start_time <= now <= self.end_time:
            self.status = 'active'
        elif now > self.end_time:
            self.status = 'finished'
        self.save()

    def __str__(self):
        if self.auction_type == 'single':
            return f'Auction for {self.product.name}'
        return f'Auction for multiple products'


class Bid(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bids_product', null=True, blank=True)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='bids_auction')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bids')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='active')  # Например, 'active', 'won', 'lost'

    def __str__(self):
        return f'Bid {self.amount} by {self.buyer} on {self.auction}'


class Chat(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='chats')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chats_as_buyer')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chats_as_seller')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Chat for {self.auction}'
