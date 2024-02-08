from rest_framework import serializers
from rest_framework.authentication import authenticate


class AuthTokenSeralizer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(trim_whitespace=False)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError("Incorrect credentials!")
        attrs["user"] = user
        return attrs
