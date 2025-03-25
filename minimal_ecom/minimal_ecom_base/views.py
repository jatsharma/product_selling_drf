from django.contrib.auth.models import Group, User
from django.contrib.auth import authenticate
from rest_framework import permissions, viewsets, status, mixins
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.utils import timezone
from django.db.models import Q
from django.shortcuts import get_object_or_404

from minimal_ecom_base.serializers import GroupSerializer, UserSerializer, ProductSerializer
from minimal_ecom_base.models import Product


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class ProductViewSet(mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):
    """
    API endpoint that allows products to be viewed and bought.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This overrides the default queryset to show all non-expired products
        """
        current_time = timezone.now()
        return Product.objects.filter(
            Q(expire_at__isnull=True) | Q(expire_at__gt=current_time)
        ).order_by('-created_at')

    def get_object(self):
        """
        This overrides the default get_object to handle 404 for expired products
        """
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj

    def perform_create(self, serializer):
        """
        This overrides the default create to set the created_by field
        """
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def buy(self, request, pk=None):
        """
        Buy a product. Only works if the product hasn't been bought yet.
        """
        product = self.get_object()
        
        if product.is_sold:
            return Response(
                {'error': 'This product has already been bought'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        product.bought_by = request.user
        product.bought_time = timezone.now()
        product.expire_at = None  # Remove expiration when bought
        product.save()
        
        return Response({
            'status': 'Product bought successfully',
            'bought_by': request.user.username,
            'bought_at': product.bought_time
        })

    @action(detail=False, methods=['get'])
    def sold_products(self, request):
        """
        List all sold products
        """
        current_time = timezone.now()
        products = Product.objects.filter(
            Q(expire_at__isnull=True) | Q(expire_at__gt=current_time),
            bought_by__isnull=False
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def unsold_products(self, request):
        """
        List all unsold products
        """
        current_time = timezone.now()
        products = Product.objects.filter(
            Q(expire_at__isnull=True) | Q(expire_at__gt=current_time),
            bought_by__isnull=True
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):
    serializer = UserSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'name': user.first_name
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'name': user.first_name
        })
    else:
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)