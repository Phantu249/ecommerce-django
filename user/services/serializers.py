from rest_framework import serializers
from .models import User, Name, Address, Ward, District, City, Role
from django.shortcuts import get_object_or_404

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name']

class DistrictSerializer(serializers.ModelSerializer):
    city = CitySerializer()

    class Meta:
        model = District
        fields = ['id', 'name', 'city']

class WardSerializer(serializers.ModelSerializer):
    district = DistrictSerializer()

    class Meta:
        model = Ward
        fields = ['id', 'name', 'district']

class AddressSerializer(serializers.ModelSerializer):
    ward = WardSerializer()

    class Meta:
        model = Address
        fields = ['id', 'detail', 'ward']

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']

class NameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Name
        fields = ['id', 'first_name', 'last_name']

class UserSerializer(serializers.ModelSerializer):
    name = NameSerializer()
    address = AddressSerializer(allow_null=True)
    role = RoleSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'name', 'address', 'role']

class UserUpdateSerializer(serializers.ModelSerializer):
    name = NameSerializer(required=False)

    class Meta:
        model = User
        fields = ['email', 'phone_number', 'name', 'address']
        extra_kwargs = {
            'email': {'required': False},
            'phone_number': {'required': False},
        }

    def update(self, instance, validated_data):
        name_data = validated_data.pop('name', None)

        # Cập nhật các trường cơ bản
        instance.email = validated_data.get('email', instance.email)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.save()

        # Cập nhật Name
        if name_data:
            name = instance.name
            name.first_name = name_data.get('first_name', name.first_name)
            name.last_name = name_data.get('last_name', name.last_name)
            name.save()

        return instance

# class AddressCreateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Address
#         fields = ['detail', 'ward_id']
#
#     def create(self, validated_data):
#         ward_id = validated_data.pop('ward_id')
#         district_id = validated_data.pop('district_id')
#         city_id = validated_data.pop('city_id')
#
#         # Kiểm tra và lấy hoặc tạo City, District, Ward
#         city = get_object_or_404(City, id=city_id)
#         district = get_object_or_404(District, id=district_id, city=city)
#         ward = get_object_or_404(Ward, id=ward_id, district=district)
#
#         address = Address.objects.create(ward=ward, **validated_data)
#         return address