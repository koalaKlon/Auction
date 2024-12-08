from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db.models import Avg

from .models import Product, Auction, Category, User, Bid, Chat, Rating, AuctionProduct


# === Custom Forms === #
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
                raise ValidationError("Для одиночного аукциона выберите один продукт.")
            if products.exists():
                raise ValidationError("Для одиночного аукциона нельзя выбирать несколько продуктов.")
        elif auction_type == 'multiple':
            if not products.exists():
                raise ValidationError("Для множественного аукциона выберите хотя бы один продукт.")
            if product:
                raise ValidationError("Для множественного аукциона нельзя выбирать только один продукт.")
        return cleaned_data


# === Inline Models === #
class AuctionProductInline(admin.TabularInline):
    model = AuctionProduct
    extra = 1
    verbose_name = "Продукт в аукционе"
    verbose_name_plural = "Продукты в аукционе"


class BidInline(admin.TabularInline):
    model = Bid
    extra = 1


class ChatInline(admin.TabularInline):
    model = Chat
    extra = 1


# === Model Admins === #
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'description', 'is_active', 'seller', 'starting_price')
    search_fields = ('name', 'description', 'seller__username')
    list_filter = ('category', 'is_active', 'created_at')
    ordering = ('-created_at',)
    fields = ('name', 'description', 'category', 'seller', 'image', 'starting_price', 'is_active')
    actions = ['delete_selected']


@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    form = AuctionForm
    inlines = [AuctionProductInline, BidInline, ChatInline]

    list_display = ('id', 'auction_type_display', 'status', 'start_time', 'end_time', 'seller', 'current_bid')
    list_filter = ('auction_type', 'status', 'start_time', 'end_time')
    search_fields = ('id', 'seller__username')
    ordering = ('-start_time',)
    fields = (
        'auction_type', 'product', 'products', 'is_favorite',
        'start_time', 'end_time', 'status', 'banner_image', 'seller', 'buyer', 'current_bid'
    )
    actions = ['delete_selected']

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
    list_display = ('username', 'email', 'role', 'is_active', 'is_blocked', 'phone_number', 'rating', 'profile_picture')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'email', 'phone_number')

    actions = ['block_users', 'unblock_users']  # Действия для блокировки и разблокировки пользователей

    def is_blocked(self, obj):
        return obj.role == 'blocked'
    is_blocked.boolean = True
    is_blocked.short_description = 'Blocked'

    def block_users(self, request, queryset):
        """Блокировка выбранных пользователей."""
        queryset.update(role='blocked', is_active=False)
        self.message_user(request, "Пользователи заблокированы.")
    block_users.short_description = "Заблокировать выбранных пользователей"

    def unblock_users(self, request, queryset):
        """Разблокировка выбранных пользователей."""
        queryset.update(role='user', is_active=True)
        self.message_user(request, "Пользователи разблокированы.")
    unblock_users.short_description = "Разблокировать выбранных пользователей"



@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'rated_user', 'rating', 'comment', 'created_at')
    search_fields = ('user__username', 'rated_user__username')
    list_filter = ('rating', 'created_at')
    ordering = ('-created_at',)
    actions = ['delete_selected']


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('id', 'auction', 'buyer', 'amount', 'timestamp')
    search_fields = ('auction__id', 'buyer__username')
    ordering = ('-timestamp',)
    actions = ['delete_selected']


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'auction', 'buyer', 'seller', 'timestamp')
    search_fields = ('auction__id', 'buyer__username', 'seller__username')
    list_filter = ('timestamp',)
    ordering = ('-timestamp',)
    actions = ['delete_selected']


@admin.register(AuctionProduct)
class AuctionProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'auction', 'product')
    search_fields = ('auction__id', 'product__name')
    list_filter = ('auction',)
    ordering = ('-id',)
    actions = ['delete_selected']


