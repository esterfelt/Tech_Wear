from django.contrib import admin
from .models import Category, Product, Review


class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ("rating",)


admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Review)
