from http.client import responses

from django.contrib.messages import success
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator
from .models import Product, ProductImage, Category
from .serializers import ProductSerializer, ProductCreateUpdateSerializer, CategorySerializer, \
    ProductSerializerNotDetail
from .permissions import IsAdminRole


class ProductDetailView(APIView):
    def get(self, request, id):
        details = bool(request.query_params.get('details', False))
        try:
            product = Product.objects.get(id=int(id))
            if details:
                serializer = ProductSerializer(product, context={'request': request})
            else:
                serializer = ProductSerializerNotDetail(product, context={'request': request})
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, id):
        permission_classes = [IsAdminRole]

        try:
            product = Product.objects.get(id=int(id))
            serializer = ProductCreateUpdateSerializer(product, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(ProductSerializer(product).data, status=status.HTTP_202_ACCEPTED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Product.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    # def delete(self, request, id):
    #     permission_classes = [IsAdminRole]
    #
    #     try:
    #         product = Product.objects.get(id=int(id))
    #         product.delete()
    #         return Response(status=status.HTTP_202_ACCEPTED)
    #     except Product.DoesNotExist:
    #         return Response(status=status.HTTP_404_NOT_FOUND)




class ProductListView(APIView):
    def get(self, request):
        query = request.query_params.get('query', '')
        category_id = request.query_params.get('category_id', None)
        per_page = int(request.query_params.get('per_page', 10))
        page = int(request.query_params.get('page', 1))

        # Lấy danh sách sản phẩm active từ database
        products = Product.objects.filter(name__icontains=query).filter(is_active__in=[True]).order_by('id')
        if category_id:
            products = products.filter(category_id=int(category_id))

        paginator = Paginator(products, per_page)
        page_obj = paginator.get_page(page)

        serializer = ProductSerializer(page_obj, many=True, context={'request': request})
        return Response({
            'products': serializer.data,
            'per_page': per_page,
            'page': page,
            'total_pages': paginator.num_pages
        }, status=status.HTTP_200_OK)

    def post(self, request):
        permission_classes = [IsAdminRole]

        serializer = ProductCreateUpdateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            product = serializer.save()
            return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        permission_classes = [IsAdminRole]

        print(request.data)
        list_product_id = request.data
        success = []
        failure = []

        for product_id in list_product_id:
            try:
                product = Product.objects.get(id=int(product_id))
                if product.is_active == False:
                    failure.append({'id': product_id, 'error': 'Product already deleted'})
                    continue
                product.is_active = False
                product.save()
                success.append(product_id)
            except Product.DoesNotExist:
                failure.append({'id': product_id, 'error': 'Product not found'})
        response = {
            'success': success,
            'failure': failure,
        }
        return Response(response, status=status.HTTP_202_ACCEPTED)


class CategoryListView(APIView):
    def get(self, request):
        categories = Category.objects.all().order_by('id')
        categories = categories.filter(is_active__in=[True])

        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        permission_classes = [IsAdminRole]

        data = {'name': request.data.get('category')}
        if 'id' in request.data:
            data['id'] = request.data['id']
        try:
            category = Category.create(**data)
            return Response(CategorySerializer(category).data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        permission_classes = [IsAdminRole]
        list_category_id = request.data
        print(list_category_id)
        success = []
        failure = []
        for category_id in list_category_id:
            try:
                category = Category.objects.get(id=int(category_id))
                if category.is_active == False:
                    failure.append({'id': category_id, 'error': 'Category already deleted'})
                    continue
                category.is_active = False
                category.save()
                success.append(category_id)
            except Category.DoesNotExist:
                failure.append({'id': category_id, 'error': 'Category not found'})
        response = {
            'success': success,
            'failure': failure,
        }
        return Response(response, status=status.HTTP_202_ACCEPTED)


class CategoryDetailView(APIView):

    def delete(self, request, id):
        permission_classes = [IsAdminRole]
        try:
            category = Category.objects.get(id=int(id))
            category.delete()
            return Response(status=status.HTTP_202_ACCEPTED)
        except Category.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, id):
        permission_classes = [IsAdminRole]

        try:
            category = Category.objects.get(id=int(id))
            serializer = CategorySerializer(category, data={'id': int(id), 'name': request.data.get('name')},
                                            partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Category.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ProductStockView(APIView):
    permission_classes = [IsAdminRole]

    def patch(self, request, id):
        try:
            product = Product.objects.get(id=int(id))
            change = request.data.get('change', 0)
            product.stock += int(change)
            product.save()
            return Response(status=status.HTTP_202_ACCEPTED)
        except Product.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)