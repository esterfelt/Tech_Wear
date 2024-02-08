import os
from uuid import uuid4
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    # Ensure name is unique in case-insensitive manner before saving
    def save(self, *args, **kwargs):
        if Category.objects.filter(
            name__iexact=self.name,
        ):
            msg = f"Category with this Name ({self.name}) already exists!"
            raise ValueError(msg)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


def validate_unique_keys(value):
    """Validate product prop keys uniqueness"""
    keys = [k.lower() for k in value]
    if len(keys) != len(set(keys)):
        duplicating_keys = set([k for k in keys if keys.count(k) > 1])
        raise ValidationError(f"Property key duplication: {duplicating_keys}")


def generate_product_image_path(instance, filename):
    """Generate product image path with unique uuid filename"""
    extension = os.path.splitext(filename)[1]
    filename = f"{uuid4()}{extension}"
    return os.path.join("uploads", "product", filename)


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    brand = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(1)],
    )
    stock = models.IntegerField(validators=[MinValueValidator(0)])
    image = models.ImageField(
        upload_to=generate_product_image_path,
        blank=True,
        null=True,
    )
    rating = models.FloatField(
        blank=True,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE)
    properties = models.JSONField(
        blank=True,
        default=dict,
        validators=[validate_unique_keys],
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    # Override save to validate fields before saving.
    # Otherwise validation doesn't work when manually saving instances via ORM
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Review(models.Model):
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    commentary = models.TextField(blank=True)
    user = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            # Ensure user can leave only 1 review for the product
            models.UniqueConstraint(
                fields=["user", "product"], name="unique_user_product_review"
            )
        ]
