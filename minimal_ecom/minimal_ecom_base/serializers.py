from django.contrib.auth.models import Group, User
from rest_framework import serializers
from .models import Product


class UserSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'first_name', 'password']
        extra_kwargs = {'first_name': {'required': True}, 'email': {'required': True}}
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            password=validated_data['password']
        )
        return user


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class ProductSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')
    bought_by = serializers.ReadOnlyField(source='bought_by.username')
    is_sold = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = ['product_id', 'product_name', 'created_by', 'created_at', 'bought_time', 'bought_by', 'is_sold', 'is_visible']
        read_only_fields = ['product_id', 'created_at', 'bought_time', 'bought_by', 'is_sold']