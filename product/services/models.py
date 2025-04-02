from djongo import models

class Counter(models.Model):
    _id = models.CharField(max_length=50, primary_key=True)  # Tên collection (product, category, product_image)
    sequence_value = models.IntegerField(default=0)

    class Meta:
        db_table = 'counters'

    @staticmethod
    def get_next_sequence(name):
        counter, created = Counter.objects.get_or_create(_id=name, defaults={'sequence_value': 1})
        if not created:
            counter.sequence_value += 1
            counter.save()
        return counter.sequence_value

class Category(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'categories'

    @classmethod
    def create(cls, **kwargs):
        if 'id' not in kwargs or kwargs['id'] is None:
            kwargs['id'] = Counter.get_next_sequence('category')
        if cls.objects.filter(id=kwargs['id']).exists():
            raise ValueError(f"ID {kwargs['id']} đã tồn tại")
        return cls.objects.create(**kwargs)

class Product(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.FloatField(default=0.0)
    description = models.CharField(max_length=255)
    category_id = models.IntegerField()
    stock = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'products'

    @classmethod
    def create(cls, **kwargs):
        if 'id' not in kwargs or kwargs['id'] is None:
            kwargs['id'] = Counter.get_next_sequence('product')
        if cls.objects.filter(id=kwargs['id']).exists():
            raise ValueError(f"ID {kwargs['id']} đã tồn tại")
        return cls.objects.create(**kwargs)

class ProductImage(models.Model):
    id = models.IntegerField(primary_key=True)
    path = models.CharField(max_length=255)
    product_id = models.IntegerField()

    def __str__(self):
        return self.path

    class Meta:
        db_table = 'product_images'

    @classmethod
    def create(cls, **kwargs):
        if 'id' not in kwargs or kwargs['id'] is None:
            kwargs['id'] = Counter.get_next_sequence('product_image')
        if cls.objects.filter(id=kwargs['id']).exists():
            raise ValueError(f"ID {kwargs['id']} đã tồn tại")
        return cls.objects.create(**kwargs)