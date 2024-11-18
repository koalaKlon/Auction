from django.shortcuts import get_object_or_404
from rest_framework import status

from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view
from .models import Product, Auction
from .serializers import ProductSerializer, AuctionSerializer, RegisterSerializer, LoginSerializer


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
    """Регистрирует нового пользователя"""
    if request.method == 'POST':
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User created successfully"}, status=201)
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


