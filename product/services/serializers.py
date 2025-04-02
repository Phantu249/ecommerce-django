from rest_framework import serializers
from django.conf import settings
import os

from urllib3 import request

from .models import Product, ProductImage, Category


class ProductImageSerializer(serializers.ModelSerializer):
    path = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'path']

    def get_path(self, obj):
        # Trả về absolute URL cho frontend
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f"{settings.MEDIA_URL}product_images/{obj.path}")
        return f"{settings.MEDIA_URL}product_images/{obj.path}"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'is_active']


class ProductSerializer(serializers.ModelSerializer):
    # product_image = ProductImageSerializer(many=True, read_only=True)
    product_image = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'description', 'product_image', 'stock', 'category', 'is_active']

    def get_product_image(self, obj):
        request = self.context.get('request')
        images = ProductImage.objects.filter(product_id=obj.id)
        return ProductImageSerializer(images, many=True, context={'request': request}).data  # Chuyển danh sách ảnh thành JSON

    def get_category(self, obj):
        try:
            category = Category.objects.get(id=obj.category_id)
            return CategorySerializer(category).data
        except Category.DoesNotExist:
            return None

class ProductSerializerNotDetail(serializers.ModelSerializer):
    img_url = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'description', 'img_url', 'stock', 'category', 'is_active']

    def get_category(self, obj):
        try:
            category = Category.objects.get(id=obj.category_id)
            return CategorySerializer(category).data
        except Category.DoesNotExist:
            return None

    def get_img_url(self, obj):
        first_image = ProductImage.objects.filter(product_id=obj.id).first()
        if first_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f"{settings.MEDIA_URL}product_images/{first_image.path}")
            return f"{settings.MEDIA_URL}product_images/{first_image.path}"
        return None


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    product_images = serializers.ListField(
        child=serializers.FileField(), write_only=True, required=False
    )
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'description', 'stock', 'category_id', 'product_images']

    def create(self, validated_data):
        product_images = validated_data.pop('product_images', [])
        try:
            product = Product.create(**validated_data)
        except ValueError as e:
            raise serializers.ValidationError(str(e))

        # Lưu ảnh vào media/product_images
        for image in product_images:
            file_path = os.path.join(settings.MEDIA_ROOT, 'product_images', image.name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)
            ProductImage.create(product_id=product.id, path=image.name)
        return product

    def update(self, instance, validated_data):
        product_images = validated_data.pop('product_images', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if product_images is not None:
            # Xóa ảnh cũ
            ProductImage.objects.filter(product_id=instance.id).delete()
            # Lưu ảnh mới
            for image in product_images:
                file_path = os.path.join(settings.MEDIA_ROOT, 'product_images', image.name)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'wb+') as destination:
                    for chunk in image.chunks():
                        destination.write(chunk)
                ProductImage.create(product_id=instance.id, path=image.name)
        return instance