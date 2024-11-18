from django.shortcuts import get_object_or_404
from rest_framework import status

from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, parser_classes
from .models import Product, Auction, Rating
from .serializers import ProductSerializer, AuctionSerializer, RegisterSerializer, LoginSerializer, \
    UserProfileSerializer
from rest_framework.parsers import MultiPartParser, FormParser


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