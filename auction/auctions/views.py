from decimal import Decimal

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils.timezone import make_aware
from datetime import datetime
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.contrib.auth import get_user_model
from .models import Product, Auction, Rating, Category, AuctionProduct
from .serializers import ProductSerializer, AuctionSerializer, RegisterSerializer, LoginSerializer, \
    UserProfileSerializer, CategorySerializer


User = get_user_model()


# API для получения списка продуктов
@api_view(['GET'])
def product_list(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def auction_list(request):
    if request.method == 'GET':
        # Используем prefetch_related для связи через AuctionProduct
        auctions = Auction.objects.prefetch_related('related_products').all()
        serializer = AuctionSerializer(auctions, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def auction_detail(request, pk):
    try:
        auction = Auction.objects.select_related('seller').prefetch_related('related_products').get(pk=pk)
    except Auction.DoesNotExist:
        return Response({'error': 'Auction not found'}, status=status.HTTP_404_NOT_FOUND)

    # Определяем продукты в зависимости от типа аукциона
    if auction.auction_type == 'multiple':
        products_data = ProductSerializer(auction.related_products.all(), many=True).data
        product_data = None
    else:
        product = auction.related_products.first()
        product_data = ProductSerializer(product).data if product else None
        products_data = None

    auction_serializer = AuctionSerializer(auction)

    # Собираем итоговые данные
    auction_data = auction_serializer.data

    # Добавляем данные продуктов в зависимости от типа аукциона
    if auction.auction_type == 'multiple':
        auction_data['products'] = products_data
    else:
        auction_data['product'] = product_data

    # Приведение типов (например, Decimal → строка)
    if isinstance(auction_data.get('starting_price'), Decimal):
        auction_data['starting_price'] = str(auction_data['starting_price'])

    print(auction_data)
    return Response(auction_data)




@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def register(request):
    """Регистрирует нового пользователя и возвращает токены"""
    if request.method == 'POST':
        # Получаем данные из запроса
        serializer = RegisterSerializer(data=request.data)

        # Проверяем, валидны ли данные
        if serializer.is_valid():
            # Создаем нового пользователя
            user = serializer.save()

            # Генерация токенов для нового пользователя
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            # Возвращаем ответ с токенами
            return Response({
                "message": "User created successfully",
                "refresh": str(refresh),
                "access": str(access_token)
            }, status=201)

        # Если данные не валидны, выводим ошибки
        print("Ошибка валидации:", serializer.errors)  # Добавлено логирование ошибок
        return Response(serializer.errors, status=400)



@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return Response({
            'message': 'Login successful',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })
    return Response({'error': 'Invalid credentials'}, status=400)


@api_view(['GET'])
def profile(request):
    """Возвращает информацию о текущем пользователе"""
    user = request.user  # Получаем текущего аутентифицированного пользователя
    profile_data = {
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'phone_number': user.phone_number,
    }

    # Добавляем profile_picture только если оно существует
    if user.profile_picture:
        profile_data['profile_picture'] = user.profile_picture.url
    else:
        profile_data['profile_picture'] = None

    return Response(profile_data)


@api_view(['PUT'])
def update_profile(request):
    user = request.user
    serializer = UserProfileSerializer(user, data=request.data, partial=True)

    if serializer.is_valid():
        user = serializer.save()  # Сохраняем данные
        print("Updated user:", user)  # Логирование данных после сохранения
        return Response(serializer.data)  # Возвращаем обновленные данные
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def rate_user(request, user_id):
    """Выставить рейтинг другому пользователю."""
    if not request.user.is_authenticated:
        return Response({'error': 'Неавторизованный доступ'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        rated_user = request.User.objects.get(id=user_id)  # Получаем пользователя, которому выставляется рейтинг
    except request.User.DoesNotExist:
        return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)

    rating_value = request.data.get('rating')
    if not rating_value or not (0 <= float(rating_value) <= 5):
        return Response({'error': 'Рейтинг должен быть числом от 0 до 5'}, status=status.HTTP_400_BAD_REQUEST)

    # Создаем рейтинг
    Rating.objects.create(user=request.user, rated_user=rated_user, rating=rating_value)

    # Пересчитываем средний рейтинг у пользователя
    rated_user.calculate_average_rating()

    return Response({'message': 'Рейтинг успешно выставлен'}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_auction(request):
    user = request.user
    data = request.data

    auction_type = data.get('auction_type', 'single')
    status_field = data.get('status', 'planned')

    try:
        start_time = make_aware(datetime.strptime(data['start_time'], "%Y-%m-%dT%H:%M"))
        end_time = make_aware(datetime.strptime(data['end_time'], "%Y-%m-%dT%H:%M"))
    except KeyError:
        return Response({'error': 'start_time and end_time are required'}, status=status.HTTP_400_BAD_REQUEST)

    # Создание аукциона
    auction = Auction.objects.create(
        auction_type=auction_type,
        seller=user,
        start_time=start_time,
        end_time=end_time,
        status=status_field
    )

    # Работа с одним продуктом
    if auction_type == 'single':
        if 'name' in data and 'description' in data and 'startingPrice' in data:
            category_id = data.get('category')
            if not category_id:
                return Response({'error': 'Category is required for creating a product'},
                                 status=status.HTTP_400_BAD_REQUEST)
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

            product = Product.objects.create(
                name=data['name'],
                description=data['description'],
                starting_price=data['startingPrice'],
                category=category,
                seller=user
            )
        else:
            product_id = data.get('product')
            if not product_id:
                return Response({'error': 'Product ID or product details are required'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        # Связываем продукт с аукционом
        AuctionProduct.objects.create(auction=auction, product=product)

    else:  # Работа с несколькими продуктами
        new_products_data = data.get('new_products', [])
        created_products = []

        for product_data in new_products_data:
            if isinstance(product_data, dict):  # Если продукт передан в виде словаря, создаём его
                category_id = product_data.get('category')
                if not category_id:
                    return Response({'error': 'Category is required for new product creation'},
                                    status=status.HTTP_400_BAD_REQUEST)
                try:
                    category = Category.objects.get(id=category_id)
                except Category.DoesNotExist:
                    return Response({'error': f'Category with ID {category_id} not found'},
                                    status=status.HTTP_404_NOT_FOUND)
                product = Product.objects.create(
                    name=product_data['name'],
                    description=product_data['description'],
                    starting_price=product_data['starting_price'],
                    category=category,
                    seller=user
                )
                created_products.append(product)
            elif isinstance(product_data, int):  # Если передан ID продукта, добавляем его
                try:
                    product = Product.objects.get(id=product_data)
                    created_products.append(product)
                except Product.DoesNotExist:
                    return Response({'error': f'Product with ID {product_data} not found'},
                                    status=status.HTTP_404_NOT_FOUND)

        # Проверка наличия продуктов для аукциона
        if not created_products:
            return Response({'error': 'No valid products found for the auction'}, status=status.HTTP_400_BAD_REQUEST)

        # Создание связей между аукционом и продуктами
        for product in created_products:
            AuctionProduct.objects.create(auction=auction, product=product)

    # Ответ успешного создания аукциона
    return Response({'message': 'Auction created successfully', 'auction_id': auction.id}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_product(request):
    user = request.user
    data = request.data

    # Проверяем, указана ли категория
    if not data.get('category'):
        return Response({'error': 'Category is required'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = ProductSerializer(data=data)
    if serializer.is_valid():
        serializer.save(seller=user)  # Устанавливаем текущего пользователя как продавца
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def get_categories(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_token(request):
    # Проверяем, есть ли refresh_token в запросе
    refresh_token = request.data.get('refresh_token', None)
    if not refresh_token:
        return Response({'error': 'Refresh token not provided'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        refresh = RefreshToken(refresh_token)
        access_token = refresh.access_token
        return Response({
            'access_token': str(access_token),
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': 'Invalid refresh token'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def user_profile_view(request, user_id):
    try:
        # Используем модель пользователя напрямую
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    # Сериализуем данные пользователя
    serializer = UserProfileSerializer(user)
    return Response(serializer.data)
