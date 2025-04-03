from django.core.paginator import Paginator
from django.db.transaction import atomic
from django.utils.translation.trans_real import translation
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password, check_password
from .models import User, Name, Address, Ward, District, City, Role
from .serializers import UserSerializer, UserUpdateSerializer, AddressSerializer, WardSerializer, DistrictSerializer, CitySerializer

class LoginView(APIView):
    permission_classes = [AllowAny]

    @atomic
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        try:
            user = User.objects.get(username=username)
            if check_password(password, user.password):
                refresh = RefreshToken.for_user(user)
                return Response({
                    'token': str(refresh.access_token)
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'error': "Account does not exist" }, status=status.HTTP_401_UNAUTHORIZED)

class RegisterView(APIView):
    permission_classes = [AllowAny]

    @atomic
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        phone_number = request.data.get('phone_number')

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        name = Name.objects.create(last_name=username)
        role = Role.objects.get_or_create(name='CUSTOMER')[0]

        user = User.objects.create_user(
            username=username,
            email=email,
            phone_number=phone_number,
            password=password,
            name=name,
            role=role
        )

        refresh = RefreshToken.for_user(user)
        return Response({
            'token': str(refresh.access_token)
        }, status=status.HTTP_200_OK)

class GetUserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateUserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    @atomic
    def put(self, request):
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @atomic
    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not check_password(old_password, user.password):
            return Response({'error': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

        user.password = make_password(new_password)
        user.save()
        return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)

class GetWardsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        id = request.query_params.get('id')
        if id:
            wards = Ward.objects.filter(id=id)
            if not wards.exists():
                return Response({'error': 'Ward not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = WardSerializer(wards, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            page = request.query_params.get('page', 1)
            per_page = request.query_params.get('per_page', 10)
            district_id = request.query_params.get('district_id')
            if district_id:
                wards = Ward.objects.filter(district_id=district_id)
            else:
                wards = Ward.objects.all()
            paginator = Paginator(wards, per_page)
            try:
                wards_page = paginator.page(page)
            except Exception as e:
                return Response({'error': 'Invalid page number'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = WardSerializer(wards_page, many=True)
            total_pages = paginator.num_pages
            response_data = {
                'wards': serializer.data,
                'page': page,
                'total_pages': total_pages,
            }
        return Response(response_data, status=status.HTTP_200_OK)

class GetDistrictsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        page = request.query_params.get('page', 1)
        per_page = request.query_params.get('per_page', 10)
        city_id = request.query_params.get('city_id')
        if city_id:
            districts = District.objects.filter(city_id=city_id)
        else:
            districts = District.objects.all()
        paginator = Paginator(districts, per_page)
        try:
            districts_page = paginator.page(page)
        except Exception as e:
            return Response({'error': 'Invalid page number'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = DistrictSerializer(districts_page, many=True)
        total_pages = paginator.num_pages
        response_data = {
            'districts': serializer.data,
            'page': page,
            'total_pages': total_pages,
        }
        return Response(response_data, status=status.HTTP_200_OK)

class GetCitiesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        page = request.query_params.get('page', 1)
        per_page = request.query_params.get('per_page', 10)

        cities = City.objects.all()
        paginator = Paginator(cities, per_page)
        try:
            cities_page = paginator.page(page)
        except Exception as e:
            return Response({'error': 'Invalid page number'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = CitySerializer(cities_page, many=True)
        total_pages = paginator.num_pages

        response_data = {
            'cities': serializer.data,
            'page': page,
            'total_pages': total_pages,
        }
        return Response(response_data, status=status.HTTP_200_OK)

class AddressView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        id = request.query_params.get('id')
        page = request.query_params.get('page', 1)
        per_page = request.query_params.get('per_page', 10)

        if id:
            address = Address.objects.filter(id=id)
            if not address.exists():
                return Response({'error': 'Address not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = AddressSerializer(address, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            addresses = Address.objects.all()
            paginator = Paginator(addresses, per_page)
            try:
                addresses_page = paginator.page(page)
            except Exception as e:
                return Response({'error': 'Invalid page number'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = AddressSerializer(addresses_page, many=True)
            total_pages = paginator.num_pages
            response_data = {
                'addresses': serializer.data,
                'page': page,
                'total_pages': total_pages,
            }
            return Response(response_data, status=status.HTTP_200_OK)

    @atomic
    def post(self, request):
        detail = request.data.get('detail')
        ward_id = request.data.get('ward_id')
        district_id = request.data.get('district_id')
        city_id = request.data.get('city_id')

        if not detail or not ward_id or not district_id or not city_id:
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            ward = get_object_or_404(Ward, id=ward_id)
            district = get_object_or_404(District, id=district_id)
            city = get_object_or_404(City, id=city_id)
        except Exception as e:
            return Response({'error': 'Invalid ID'}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        if user.address:
            user.address.detail = detail
            user.address.ward = ward
            user.save()
        else:
            address = Address.objects.create(detail=detail, ward=ward)
            # Assign the address to the user
            user.address = address
            user.save()
        serializer = AddressSerializer(user.address)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


