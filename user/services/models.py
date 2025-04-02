from django.db import models

class City(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class District(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    city = models.ForeignKey(City, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Ward(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    district = models.ForeignKey(District, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Address(models.Model):
    id = models.AutoField(primary_key=True)
    detail = models.CharField(max_length=255)
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.detail}, {self.ward.name}"

class Role(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Name(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255, default='')
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, username, email, phone_number, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, phone_number=phone_number, **extra_fields)
        user.name = Name.objects.create(last_name=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('role', Role.objects.get_or_create(name='ADMIN')[0])
        return self.create_user(username, email, phone_number, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=255)
    name = models.ForeignKey(Name, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'phone_number']

    def __str__(self):
        return self.username
