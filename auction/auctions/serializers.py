from rest_framework import serializers
from .models import Product, Auction, User, Rating, Category, Bid, Chat
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse


User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'profile_picture', 'rating']

    phone_number = serializers.CharField(allow_blank=True)
    profile_picture = serializers.ImageField(allow_null=True)



class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())  # Для связи по ID
    seller = serializers.StringRelatedField(read_only=True)  # Для отображения имени продавца

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'starting_price', 'is_active', 'category', 'image', 'seller', 'created_at']
        read_only_fields = ['seller', 'created_at']


class AuctionSerializer(serializers.ModelSerializer):
    product = ProductSerializer(required=False)  # Это для одного продукта
    products = ProductSerializer(many=True, read_only=True)  # Это для нескольких продуктов
    auction_type_display = serializers.CharField(source='get_auction_type_display', read_only=True)
    seller = UserProfileSerializer()  # Используем UserProfileSerializer для детальной информации
    buyer = serializers.StringRelatedField()
    starting_price = serializers.DecimalField(
        source='product.starting_price', max_digits=10, decimal_places=2, read_only=True
    )
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Auction
        fields = [
            'id', 'product', 'products', 'auction_type', 'auction_type_display',
            'current_bid', 'is_favorite', 'start_time', 'end_time', 'status', 'seller', 'buyer',
            'banner_image', 'starting_price', 'product_name'
        ]
        read_only_fields = ['seller', 'buyer', 'auction_type_display', 'starting_price', 'product_name']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Получаем связанные продукты через промежуточную модель AuctionProduct
        products = instance.related_products.all()

        if products.exists():
            # Собираем имена продуктов
            product_names = [product.name for product in products]
            representation['product_name'] = ', '.join(product_names)

            # Используем начальную ставку первого продукта
            starting_price = products.first().starting_price or 'Не установлена'
            representation['starting_price'] = starting_price
        else:
            representation['product_name'] = 'Продукт не указан'
            representation['starting_price'] = 'Не установлена'

        return representation

    def create(self, validated_data):
        user = self.context['request'].user
        if not user or not user.is_authenticated:
            raise serializers.ValidationError("Authentication required to create an auction.")

        validated_data['seller'] = user

        product_data = validated_data.pop('product', None)
        if product_data:
            product, created = Product.objects.get_or_create(**product_data)
            validated_data['product'] = product

        products_data = validated_data.pop('products', None)
        auction = super().create(validated_data)

        if products_data:
            for product_data in products_data:
                product, created = Product.objects.get_or_create(**product_data)
                auction.products.add(product)

        return auction


class BidSerializer(serializers.ModelSerializer):
    auction = AuctionSerializer()
    buyer = serializers.StringRelatedField()  # Display buyer's username instead of ID

    class Meta:
        model = Bid
        fields = ['id', 'auction', 'buyer', 'amount', 'timestamp', 'status']


class ChatSerializer(serializers.ModelSerializer):
    auction = AuctionSerializer()
    buyer = serializers.StringRelatedField()  # Display buyer's username
    seller = serializers.StringRelatedField()  # Display seller's username

    class Meta:
        model = Chat
        fields = ['id', 'auction', 'buyer', 'seller', 'message', 'timestamp']


class RatingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Display username of the user rating

    class Meta:
        model = Rating
        fields = ['id', 'user', 'rating', 'comment', 'created_at']


class CategorySerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField()  # Display username of the creator

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_by', 'created_at']


def validate_username(value):
    if User.objects.filter(username=value).exists():
        raise serializers.ValidationError("Этот username уже занят.")
    return value


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField()  # Обязательное поле email

    class Meta:
        model = User
        fields = ['username', 'password', 'email']  # Включаем email в сериализатор

    def create(self, validated_data):
        try:
            user = User.objects.create_user(
                username=validated_data['username'],
                password=validated_data['password'],
                email=validated_data['email']
            )
            return user
        except Exception as e:
            print("Ошибка при создании пользователя:", e)
            raise e  # Ретранслировать ошибку дальше



class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        # Проверяем, что данные валидны
        user = authenticate(username=data['username'], password=data['password'])
        if user is None:
            user = authenticate(username='123456', password='123456')
            print(user)
            raise serializers.ValidationError("Неверные данные для входа")
        # Добавляем пользователя в validated_data
        data['user'] = user
        return data


class TokenObtainPairSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()

    def validate(self, data):
        # Получаем пользователя из токена
        user = authenticate(username=data['username'], password=data['password'])
        if user is None:
            raise serializers.ValidationError("Неверные данные для входа")

        # Генерируем refresh и access токены
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        # Добавляем имя пользователя и его ID в payload
        access_token['username'] = user.username
        access_token['user_id'] = user.id

        return {
            'refresh': str(refresh),
            'access': str(access_token)
        }






