from rest_framework import serializers
from .models import Book


class BookSerializer(serializers.ModelSerializer):
    title = serializers.CharField(allow_blank=False, trim_whitespace=True)
    author = serializers.CharField(allow_blank=False, trim_whitespace=True)

    class Meta:
        model = Book
        fields = ["id", "title", "author", "price", "inventory"]

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price must be >= 0.")
        return value

    def validate_inventory(self, value):
        if value < 0:
            raise serializers.ValidationError("Inventory must be >= 0.")
        return value
