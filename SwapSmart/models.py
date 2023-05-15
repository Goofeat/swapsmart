from django.contrib.auth.models import User
from django.db import models


class Category(models.Model):
    image = models.ImageField(upload_to='categories/')
    url_name = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Ad(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='listings/', null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=12)
    condition = models.CharField(max_length=50, choices=(('new', 'New'), ('used', 'Used')))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE)