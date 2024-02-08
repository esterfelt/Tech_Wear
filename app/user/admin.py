from django.contrib import admin
from .models import User, Address, Cart, CartItem, WishItem

admin.site.register(User)
admin.site.register(Address)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(WishItem)
