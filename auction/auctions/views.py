from decimal import Decimal
from django.db.models import Q, Avg, Min, Max
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.utils.timezone import make_aware
from datetime import datetime
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.contrib.auth import get_user_model
from .models import Product, Auction, Rating, Category, AuctionProduct, Bid, Chat
from .serializers import ProductSerializer, AuctionSerializer, RegisterSerializer, LoginSerializer, \
    UserProfileSerializer, CategorySerializer, BidSerializer, ChatSerializer
from channels.layers import get_channel_layer, channel_layers
from asgiref.sync import async_to_sync


User = get_user_model()


# API для получения списка продуктов
@api_view(['GET'])
def product_list(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def auction_list(request):
    category = request.query_params.get('category')  # Фильтрация по категории
    auction_type = request.query_params.get('type')  # Фильтрация по типу аукциона
    search = request.query_params.get('search')  # Поиск по имени товара
    sort_by = request.query_params.get('sort_by', 'start_time')  # Сортировка по дате начала по умолчанию

    # Базовый QuerySet
    auctions = Auction.objects.all()

    # Фильтрация по категории (если указано)
    if category:
        auctions = auctions.filter(related_products__category__id=category)

    # Фильтрация по типу аукциона
    if auction_type:
        auctions = auctions.filter(auction_type=auction_type)

    # Поиск по имени товара
    if search:
        auctions = auctions.filter(
            Q(related_products__name__icontains=search)
        ).distinct()

    # Сортировка
    auctions = auctions.order_by(sort_by)

    # Сериализация с передачей контекста
    serializer = AuctionSerializer(auctions, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def category_list(request):
    categories = Category.objects.all()
    print(categories)
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


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
        products = auction.related_products.all()
        products_data = [
            {
                **ProductSerializer(product).data,
                'image': request.build_absolute_uri(product.image.url) if product.image else None
            }
            for product in products
        ]
        product_data = None
    else:
        product = auction.related_products.first()
        if product:
            product_data = ProductSerializer(product).data
            product_data['image'] = request.build_absolute_uri(product.image.url) if product.image else None
        else:
            product_data = None
        products_data = None

    auction_serializer = AuctionSerializer(auction)
    auction_data = auction_serializer.data

    # Проверим, существует ли изображение
    if auction.banner_image:
        banner_url = request.build_absolute_uri(auction.banner_image.url)
    else:
        banner_url = None

    auction_data['banner_image'] = banner_url

    # Добавление имени текущего лидера
    highest_bid = Bid.objects.filter(auction=auction).order_by('-amount').first()
    if highest_bid:
        auction_data['current_leader'] = highest_bid.buyer.username
        auction_data['current_bid'] = str(highest_bid.amount)
    else:
        auction_data['current_leader'] = None
        auction_data['current_bid'] = None

    if auction.status == 'finished':
        auction_data['winner'] = auction.buyer.username if auction.buyer else None
        bids = Bid.objects.filter(auction=auction).order_by('-amount')
        auction_data['all_bids'] = BidSerializer(bids, many=True).data

    if auction.auction_type == 'multiple':
        auction_data['products'] = products_data
    else:
        auction_data['product'] = product_data

    if isinstance(auction_data.get('starting_price'), Decimal):
        auction_data['starting_price'] = str(auction_data['starting_price'])

    return Response(auction_data)


@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def product_detail(request, pk):
    try:
        # Fetch the product by its primary key
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({'detail': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    # Serialize the product data
    serializer = ProductSerializer(product)

    # Return the serialized data in the response
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_auction(request, pk):
    try:
        auction = Auction.objects.get(pk=pk)
    except Auction.DoesNotExist:
        return Response({'error': 'Auction not found'}, status=status.HTTP_404_NOT_FOUND)

    # Проверка, является ли текущий пользователь владельцем аукциона
    if auction.seller != request.user:
        return Response({'error': 'You are not the seller of this auction'}, status=status.HTTP_403_FORBIDDEN)

    serializer = AuctionSerializer(auction, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_product(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    # Check if the current user is the product owner
    if product.seller != request.user:
        return Response({'error': 'You are not the seller of this product'}, status=status.HTTP_403_FORBIDDEN)

    # Merge request data with uploaded files
    data = request.data.copy()
    data.update(request.FILES)

    serializer = ProductSerializer(product, data=data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
def current_user(request):
    """Возвращает информацию о текущем пользователе по никнейму и его роль"""
    if not request.user.is_authenticated:
        return Response({'error': 'User not authenticated'},
                        status=401)  # Возвращаем ошибку, если пользователь не авторизован

    user = request.user  # Текущий аутентифицированный пользователь

    try:
        # Получаем пользователя по никнейму (username)
        user_data = User.objects.get(username=user.username)

        # Возвращаем данные пользователя вместе с его ролью
        current_user_data = {
            'id': user_data.id,
            'username': user_data.username,
            'email': user_data.email,
            'first_name': user_data.first_name,
            'last_name': user_data.last_name,
            'role': user_data.role,  # Допустим, поле 'role' существует в модели пользователя
        }
        return Response(current_user_data)

    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)


@api_view(['GET'])
def is_favorite(request, pk):
    """Проверяет, находится ли аукцион в избранном текущего пользователя"""
    user = request.user
    try:
        auction = Auction.objects.get(pk=pk)
        is_favorite = auction in user.favorite_auctions.all()
        return Response({'is_favorite': is_favorite}, status=200)
    except Auction.DoesNotExist:
        return Response({'error': 'Аукцион не найден'}, status=404)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_favorites(request, pk):
    """Удаляет аукцион из избранного текущего пользователя"""
    user = request.user
    try:
        auction = Auction.objects.get(pk=pk)
        if auction in user.favorite_auctions.all():
            user.favorite_auctions.remove(auction)
            return Response({'message': 'Аукцион удален из избранного'}, status=200)
        else:
            return Response({'error': 'Аукцион отсутствует в избранном'}, status=404)
    except Auction.DoesNotExist:
        return Response({'error': 'Аукцион не найден'}, status=404)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_favorites(request, pk):
    """Добавляет аукцион в избранное текущего пользователя"""
    user = request.user
    try:
        auction = Auction.objects.get(pk=pk)
        user.favorite_auctions.add(auction)
        return Response({'message': 'Аукцион добавлен в избранное'}, status=200)
    except Auction.DoesNotExist:
        return Response({'error': 'Аукцион не найден'}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """Возвращает информацию о текущем пользователе и его активности"""
    user = request.user

    # Получаем все ставки пользователя
    participated_bids = Bid.objects.filter(buyer=user).distinct()

    auctions_with_result = []

    for bid in participated_bids:
        auction = bid.auction
        is_winner = auction.buyer == user
        auctions_with_result.append({
            'id': auction.id,
            'auction_type': auction.auction_type,
            'start_time': auction.start_time,
            'end_time': auction.end_time,
            'banner_image': auction.banner_image.url if auction.banner_image else None,
            'status': auction.status,
            'is_winner': is_winner,
            'buyer__username': auction.buyer.username if auction.buyer else None,
        })

    profile_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'phone_number': getattr(user, 'phone_number', None),
        'rating': getattr(user, 'rating', 0),
        'profile_picture': request.build_absolute_uri(user.profile_picture.url) if user.profile_picture else None,
        'favorites': list(user.favorite_auctions.values('id', 'auction_type', 'status', 'banner_image')),
        'auctions': list(Auction.objects.filter(seller=user).values(
            'id', 'auction_type', 'start_time', 'end_time', 'banner_image', 'status'
        )),
        'participated_auctions': auctions_with_result,
        'bids_history': list(Bid.objects.filter(buyer=user).values(
            'id', 'auction_id', 'auction__auction_type', 'amount', 'timestamp', 'status'
        ).order_by('-timestamp')),
    }

    return Response(profile_data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    serializer = UserProfileSerializer(user, data=request.data, partial=True)

    if serializer.is_valid():
        user = serializer.save()  # Сохраняем данные
        return Response(serializer.data)  # Возвращаем обновленные данные
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
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

    banner_image = request.FILES.get('banner_image')
    auction = Auction.objects.create(
        auction_type=auction_type,
        seller=user,
        start_time=start_time,
        end_time=end_time,
        status=status_field,
        banner_image=banner_image
    )

    if auction_type == 'single':
        product_data = data.get('product')
        if not product_data:
            # Обработка нового продукта для одиночного типа
            new_product_data = {
                'name': data.get('new_product_name'),
                'description': data.get('new_product_description'),
                'starting_price': data.get('new_product_starting_price'),
                'category': data.get('new_product_category')
            }
            product_images = request.FILES.getlist('new_product_image')
            if not product_images:
                return Response({'error': 'No image provided for the new product'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                category = Category.objects.get(id=new_product_data['category'])
                product = Product.objects.create(
                    name=new_product_data['name'],
                    description=new_product_data['description'],
                    starting_price=new_product_data['starting_price'],
                    category=category,
                    seller=user,
                    image=product_images[0]  # Используем первое изображение
                )
                AuctionProduct.objects.create(auction=auction, product=product)
            except Category.DoesNotExist:
                return Response({'error': f"Category with id {new_product_data['category']} not found"},
                                status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error': f"Unexpected error: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Использование существующего продукта
            try:
                product = Product.objects.get(id=product_data)
                AuctionProduct.objects.create(auction=auction, product=product)
            except Product.DoesNotExist:
                return Response({'error': f'Product with id {product_data} not found'}, status=status.HTTP_400_BAD_REQUEST)

    elif auction_type == 'multiple':
        created_products = []
        errors = []
        idx = 0

        while f'new_products[{idx}][name]' in data:
            try:
                product_data = {
                    'name': data[f'new_products[{idx}][name]'],
                    'description': data[f'new_products[{idx}][description]'],
                    'starting_price': data[f'new_products[{idx}][starting_price]'],
                    'category': data[f'new_products[{idx}][category]']
                }
                product_images = request.FILES.getlist(f'new_products[{idx}][image]')
                if not product_images:
                    raise ValueError(f"No image provided for product {idx}")

                category = Category.objects.get(id=product_data['category'])
                product = Product.objects.create(
                    name=product_data['name'],
                    description=product_data['description'],
                    starting_price=product_data['starting_price'],
                    category=category,
                    seller=user,
                    image=product_images[0]  # Используем первое изображение
                )
                AuctionProduct.objects.create(auction=auction, product=product)
                created_products.append(product.id)
            except Category.DoesNotExist:
                errors.append(f"Category with id {product_data.get('category')} not found for product {idx}")
            except ValueError as e:
                errors.append(str(e))
            except Exception as e:
                errors.append(f"Unexpected error for product {idx}: {e}")
            idx += 1

        return Response({
            'message': 'Auction created successfully',
            'auction_id': auction.id,
            'created_products': created_products,
            'errors': errors
        }, status=status.HTTP_201_CREATED)

    return Response({'message': 'Auction created successfully', 'auction_id': auction.id},
                    status=status.HTTP_201_CREATED)


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
        serializer.save(seller=user)
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
        user = User.objects.get(pk=user_id)
        auctions = Auction.objects.filter(seller=user)  # Получаем аукционы пользователя
        auctions_data = [
            {
                "id": auction.id,
                "auction_type": auction.auction_type,
                "start_time": auction.start_time,
                "end_time": auction.end_time,
                "banner_image": auction.banner_image.url if auction.banner_image else None,
                "status": auction.status,
            }
            for auction in auctions
        ]

        profile_data = {
            "id": user.id,
            "username": user.username,
            "rating": user.rating,
            "email": user.email,
            "phone_number": user.phone_number,
            "profile_picture": request.build_absolute_uri(user.profile_picture.url) if user.profile_picture else None,
            "auctions": auctions_data,  # Добавляем аукционы в ответ
        }
        return Response(profile_data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rate_user(request, user_id):
    try:
        rated_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

    # Запрет на выставление рейтинга самому себе
    if rated_user.id == request.user.id:
        return Response({"error": "Вы не можете оценивать себя"}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'POST':
        rating_value = request.data.get('rating')
        if rating_value is None or not (1 <= float(rating_value) <= 10):
            return Response({"error": "Рейтинг должен быть числом от 1 до 10"}, status=status.HTTP_400_BAD_REQUEST)
        # Проверяем, выставлял ли пользователь уже рейтинг
        existing_rating = Rating.objects.filter(user=request.user, rated_user=rated_user).first()

        if existing_rating:
            # Обновляем существующий рейтинг
            existing_rating.rating = rating_value
            existing_rating.save()
        else:
            # Создаем новый рейтинг
            Rating.objects.create(
                user=request.user,
                rated_user=rated_user,
                rating=rating_value
            )

        # Пересчитываем средний рейтинг
        rated_user.calculate_average_rating()

        return Response({
            "message": "Рейтинг успешно установлен",
            "updated_rating": rated_user.rating
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def auction_status(request):
    auctions = Auction.objects.filter(start_time__lte=timezone.now())
    for auction in auctions:
        auction.update_status()
    data = AuctionSerializer(auctions, many=True).data
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_bid(request, pk):
    try:
        auction = Auction.objects.get(pk=pk, status='active')
        buyer = request.user
        amount = request.data.get('amount')

        # Проверяем, что сумма ставки передана и больше текущей
        if amount is None or Decimal(amount) <= (auction.current_bid or Decimal(0)):
            return Response({"error": "Ставка должна быть больше текущей!"}, status=status.HTTP_400_BAD_REQUEST)

        # Преобразуем сумму в Decimal
        amount = Decimal(amount)

        # Обновляем текущую ставку в аукционе
        auction.place_bid(buyer, amount)

        # Создаём запись в таблице Bid
        bid = Bid.objects.create(
            auction=auction,
            buyer=buyer,
            amount=amount,
        )

        # Находим нового лидера
        current_leader = buyer.username

        # Отправляем уведомление через WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'auction_{pk}',
            {
                'type': 'auction_update',
                'message': {
                    "current_bid": str(auction.current_bid),
                    "current_leader": current_leader,
                }
            }
        )

        return Response({
            "message": "Ставка успешно принята!",
            "current_bid": auction.current_bid,
            "current_leader": current_leader,
            "bid_id": bid.id,
        })

    except Auction.DoesNotExist:
        return Response({"error": "Аукцион не найден или завершён."}, status=status.HTTP_404_NOT_FOUND)
    except ValueError:
        return Response({"error": "Некорректная сумма ставки."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_user_role(request):
    user = request.user  # Получаем текущего авторизованного пользователя
    current_role = user.role  # Предполагается, что в модели есть поле role

    if current_role == 'user':
        user.role = 'seller'  # Меняем роль на продавца
    elif current_role == 'seller':
        user.role = 'user'
    else:
        return Response({'error': 'Invalid role change'}, status=status.HTTP_400_BAD_REQUEST)

    user.save()  # Сохраняем изменения в базе данных
    return Response({'message': f'Role changed to {user.role}'})


@api_view(['GET'])
@permission_classes([IsAdminUser])
def stats_view(request):
    stats = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'total_products': Product.objects.count(),
        'active_auctions': Auction.objects.filter(status="active").count(),
        'total_bids': Bid.objects.count(),
        'average_bid': Bid.objects.aggregate(Avg('amount'))['amount__avg'] or 0,
        'min_bid': Bid.objects.aggregate(Min('amount'))['amount__min'] or 0,
        'max_bid': Bid.objects.aggregate(Max('amount'))['amount__max'] or 0,
    }
    return Response(stats, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_messages(request, auction_id):
    messages = Chat.objects.filter(auction_id=auction_id).order_by('timestamp')
    data = [{"sender_name": msg.sender_name, "message": msg.message} for msg in messages]
    return JsonResponse(data, safe=False)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request):
    auction_id = request.data.get('auction_id')
    message = request.data.get('message')

    if not auction_id or not message:
        return Response({'error': 'Auction ID and message are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        auction = Auction.objects.get(id=auction_id)
        buyer = auction.buyer
        seller = auction.seller
    except Auction.DoesNotExist:
        return Response({'error': 'Auction not found'}, status=status.HTTP_404_NOT_FOUND)

    # Ensure the sender is correctly identified as buyer or seller
    sender_name = buyer.username if request.user == buyer else seller.username
    async_to_sync(get_channel_layer().group_send)(
        f"auction_{auction_id}_chat",
        {
            'type': 'chat_message',
            'message': message,
            'sender_name': sender_name
        }
    )
    # Create a new chat message in the database
    chat = Chat.objects.create(
        auction=auction,
        buyer=buyer,
        seller=seller,
        message=message,
        sender_name=sender_name
    )

    return Response({'success': 'Message sent'}, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_product(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    # Проверяем, является ли пользователь продавцом или админом
    if product.seller != request.user and request.user.username != 'admin':
        return Response({'error': 'You are not the seller of this product'}, status=status.HTTP_403_FORBIDDEN)

    # Получаем все аукционы, связанные с продуктом
    auctions = product.auctions.all()

    # Удаляем продукт
    product.delete()

    remaining_products = 0

    for auction in auctions:
        remaining_products = AuctionProduct.objects.filter(auction=auction).count()

        if remaining_products == 0:
            auction.delete()

    # Возвращаем статус 200 и данные о количестве оставшихся товаров
    return Response({
        'message': 'Product deleted successfully',
        'remaining_products': remaining_products  # Теперь отправляем данные
    }, status=status.HTTP_200_OK)



@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_auction(request, pk):
    try:
        auction = Auction.objects.get(pk=pk)
    except Auction.DoesNotExist:
        return Response({'error': 'Auction not found'}, status=status.HTTP_404_NOT_FOUND)

    # Проверяем права доступа: пользователь должен быть продавцом или админом
    if auction.seller != request.user and request.user.username != 'admin':
        return Response({'error': 'You are not authorized to delete this auction'}, status=status.HTTP_403_FORBIDDEN)

    auction.delete()
    return Response({'message': 'Auction deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

