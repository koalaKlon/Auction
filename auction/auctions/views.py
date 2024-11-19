from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from .models import Product, Auction, Rating, Category
from .serializers import ProductSerializer, AuctionSerializer, RegisterSerializer, LoginSerializer, \
    UserProfileSerializer, CategorySerializer


# API для получения списка продуктов
@api_view(['GET'])
def product_list(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
def auction_list(request):
    if request.method == 'GET':
        auctions = Auction.objects.all()
        serializer = AuctionSerializer(auctions, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = AuctionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def auction_detail(request, pk):
    auction = get_object_or_404(Auction, pk=pk)

    if request.method == 'GET':
        serializer = AuctionSerializer(auction)
        return Response(serializer.data)

    elif request.method == 'PUT':
        if auction.seller != request.user:
            return Response({'error': 'You are not the seller of this auction'}, status=status.HTTP_403_FORBIDDEN)

        serializer = AuctionSerializer(auction, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if auction.seller != request.user:
            return Response({'error': 'You are not the seller of this auction'}, status=status.HTTP_403_FORBIDDEN)

        auction.delete()
        return Response({'message': 'Auction deleted'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
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

        # Если данные не валидны, возвращаем ошибки
        return Response(serializer.errors, status=400)


@api_view(['POST'])
def login(request):
    """Логин пользователя и получение токенов"""
    if request.method == 'POST':
        print("Request data:", request.data)  # Печатаем входящие данные запроса

        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']  # Получаем пользователя из сериализатора

            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            return Response({
                'refresh': str(refresh),
                'access': str(access_token)
            })

        print("Serializer errors:", serializer.errors)  # Печатаем ошибки сериализатора
        return Response({'error': 'Неверные данные для входа', 'details': serializer.errors}, status=400)


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
@permission_classes([IsAuthenticated])  # Only authenticated users can create auctions
def create_auction(request):
    user = request.user
    data = request.data

    # Extract auction details
    auction_type = data.get('auction_type', 'single')
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    status_field = data.get('status', 'planned')

    if auction_type == 'single':
        # Check if product data exists for new product creation
        if 'name' in data and 'description' in data and 'startingPrice' in data:
            # Проверяем наличие категории
            category_id = data.get('category')
            if not category_id:
                return Response({'error': 'Category is required for creating a product'},
                                status=status.HTTP_400_BAD_REQUEST)
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

            # Создаем продукт
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

        # Create the auction for the single product
        auction = Auction.objects.create(
            auction_type=auction_type,
            product=product,
            seller=user,
            start_time=start_time,
            end_time=end_time,
            status=status_field
        )
    else:
        # For multiple products, the logic remains the same
        product_ids = data.get('products', [])
        if not product_ids:
            return Response({'error': 'Product IDs are required for multiple product auction'}, status=status.HTTP_400_BAD_REQUEST)
        products = Product.objects.filter(id__in=product_ids)

        if not products.exists():
            return Response({'error': 'No valid products found'}, status=status.HTTP_404_NOT_FOUND)

        auction = Auction.objects.create(
            auction_type=auction_type,
            seller=user,
            start_time=start_time,
            end_time=end_time,
            status=status_field
        )
        auction.products.set(products)

        # Return a success response
    return Response(
        {
            'message': 'Auction created successfully',
            'auction_id': auction.id,
            'auction_type': auction.auction_type,
            'start_time': auction.start_time,
            'end_time': auction.end_time,
            'status': auction.status,
        },
        status=status.HTTP_201_CREATED
    )


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
@permission_classes([AllowAny])  # Категории могут быть доступны всем
def get_categories(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)
