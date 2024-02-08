from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from .models import Cart, CartItem


# Create a cart for the newly created user
@receiver(post_save, sender=get_user_model())
def create_cart_for_user(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)


# If there already exists cart item with the same cart and product then
# increase the quantity of the existing one instead of creating a new one
@receiver(post_save, sender=CartItem)
def merge_same_cartitems(sender, instance, created, **kwargs):
    if not created:
        return

    existing_cartitems = CartItem.objects.filter(
        cart=instance.cart,
        product=instance.product,
    )

    if len(existing_cartitems) > 1:
        existing_cartitems[0].quantity += instance.quantity
        existing_cartitems[0].save()
        # TODO By deleting created cartitem we increase next id to 1.
        # It also may lead to performance issues. FIND SOLUTION!
        instance.delete()
