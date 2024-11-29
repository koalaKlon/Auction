import datetime
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

from django.utils.timezone import now


class User(AbstractUser):
    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('user', 'User'),
        ('manager', 'Manager')
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    rating = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    profile_picture = models.ImageField(upload_to='user_profiles/', blank=True, null=True)
    email = models.EmailField(unique=True)  # Добавление поля email
    favorite_auctions = models.ManyToManyField('Auction', related_name='favorited_by', blank=True)

    def calculate_average_rating(self):
        """Пересчитываем средний рейтинг пользователя на основе всех его рейтингов."""
        ratings = Rating.objects.filter(rated_user=self)  # Учитываем все рейтинги для данного пользователя
        if ratings:
            total_rating = sum([rating.rating for rating in ratings])
            avg_rating = total_rating / len(ratings)
            self.rating = round(avg_rating, 2)  # Обновляем поле rating с округлением до двух знаков
        else:
            self.rating = 0  # Если нет рейтингов, устанавливаем 0
        self.save()  # Сохраняем изменения в базе

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
    rating = models.DecimalField(max_digits=3, decimal_places=1)
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
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='products')
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products')
    starting_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    auctions = models.ManyToManyField('Auction', through='AuctionProduct', related_name='related_products')
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
    current_bid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_favorite = models.BooleanField(default=False)
    start_time = models.DateTimeField(default=now)
    end_time = models.DateTimeField(default=now(), null=True, blank=True)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='seller_auctions')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='buyer_auctions')
    banner_image = models.ImageField(upload_to='auction_banners/', blank=True, null=True)
    status = models.CharField(max_length=20, default='planned')

    def update_status(self):
        current_time = timezone.now()  # Получаем текущее время с учетом часового пояса
        if current_time < self.start_time:
            self.status = 'planned'
            self.save()
        elif self.start_time <= current_time <= self.end_time:
            self.status = 'active'
            self.save()
        elif current_time > self.end_time:
            self.status = 'finished'
            self.save()

    def place_bid(self, buyer, amount):
        if amount > (self.current_bid or 0):
            self.current_bid = amount
            self.buyer = buyer
            self.end_time = now() + datetime.timedelta(seconds=10)
            self.save()

    def check_if_finished(self):
        if now() > self.end_time:
            self.status = 'finished'
            self.end_time = now()
            self.save()

    def __str__(self):
        return f'Auction ({self.get_auction_type_display()})'


class AuctionProduct(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.auction} - {self.product}'


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
