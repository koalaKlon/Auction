from django import forms
from django.contrib import admin
from rest_framework.exceptions import ValidationError
from .models import Product, Auction, Category, User, Bid, Chat, Rating


class AuctionForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        auction_type = cleaned_data.get('auction_type')
        product = cleaned_data.get('product')
        products = cleaned_data.get('products')

        if auction_type == 'single':
            if not product:
                raise ValidationError("Для одиночного аукциона необходимо выбрать один продукт.")
            if products.exists():
                raise ValidationError("Для одиночного аукциона нельзя выбирать несколько продуктов.")
        elif auction_type == 'multiple':
            if not products.exists():
                raise ValidationError("Для множественного аукциона необходимо выбрать хотя бы один продукт.")
            if product:
                raise ValidationError("Для множественного аукциона нельзя выбирать только один продукт.")
        return cleaned_data


class BidInline(admin.TabularInline):
    model = Bid
    extra = 1


class ChatInline(admin.TabularInline):
    model = Chat
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'description', 'is_active', 'seller')
    search_fields = ('name', 'description')
    list_filter = ('category', 'is_active')
    ordering = ('-id',)
    fields = ('name', 'description', 'category', 'seller', 'image', 'is_active')
    actions = ['delete_selected']  # Добавление возможности массового удаления


@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    form = AuctionForm

    list_display = ('id', 'auction_type_display', 'status', 'start_time', 'end_time', 'seller')
    list_filter = ('auction_type', 'status', 'start_time')
    search_fields = ('id', 'seller__username')
    ordering = ('-start_time',)
    fields = (
        'auction_type', 'product', 'products', 'is_favorite',
        'start_time', 'end_time', 'status', 'banner_image', 'seller', 'buyer'
    )
    actions = ['delete_selected']  # Добавление возможности массового удаления

    def auction_type_display(self, obj):
        return dict(Auction.AUCTION_TYPE_CHOICES).get(obj.auction_type, 'Unknown')

    auction_type_display.short_description = 'Тип аукциона'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'created_by', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_by', 'created_at')
    ordering = ('-created_at',)
    actions = ['delete_selected']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'role', 'rating', 'is_active')
    search_fields = ('username', 'email')
    list_filter = ('role', 'is_active')
    ordering = ('-id',)
    fields = ('username', 'email', 'role', 'phone_number', 'rating', 'profile_picture', 'is_active')
    actions = ['delete_selected']


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('id', 'auction', 'buyer', 'amount', 'timestamp', 'status')
    search_fields = ('auction__id', 'buyer__username')
    list_filter = ('status', 'timestamp')
    ordering = ('-timestamp',)
    actions = ['delete_selected']


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'auction', 'buyer', 'seller', 'timestamp')
    search_fields = ('auction__id', 'buyer__username', 'seller__username')
    list_filter = ('timestamp',)
    ordering = ('-timestamp',)
    actions = ['delete_selected']


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'rating', 'created_at')
    search_fields = ('user__username',)
    list_filter = ('rating', 'created_at')
    ordering = ('-created_at',)
    actions = ['delete_selected']
