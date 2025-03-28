from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.utils import timezone
from datetime import timedelta


class Product(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products')
    product_id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    bought_time = models.DateTimeField(null=True, blank=True)
    product_name = models.CharField(max_length=255)
    bought_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='bought_products')
    expire_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.product_name} (ID: {self.product_id})"

    class Meta:
        ordering = ['-created_at']

    @property
    def is_sold(self):
        return self.bought_by is not None

    @property
    def is_visible(self):
        if self.expire_at is None:
            return True
        return timezone.now() <= self.expire_at

    def save(self, *args, **kwargs):
        if not self.expire_at and not self.is_sold:
            # Set expiration to 2 minutes from creation time
            self.expire_at = timezone.now() + timedelta(minutes=2)
        super().save(*args, **kwargs)


# This signal creates a token for each user when created
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
