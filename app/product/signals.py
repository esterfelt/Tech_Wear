from django.dispatch import receiver
from django.db.models import Avg
from django.db.models.signals import m2m_changed, post_save, post_delete
from .models import Product, Review


# Update product rating whenever review for it saved or deleted
@receiver(post_save, sender=Review)
@receiver(post_delete, sender=Review)
def update_product_rating(sender, instance, **kwargs):
    product = instance.product
    reviews = product.review_set.all()
    avg_rating_dict = reviews.aggregate(Avg("rating"))
    avg_rating = avg_rating_dict["rating__avg"]

    # If average rating is None or 0 then set 0
    product.rating = avg_rating or 0
    product.save()
