from rest_framework import serializers
from .models import Recipe, Monotub


class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = '__all__'


class MonotubSerializer(serializers.ModelSerializer):

    class Meta:
        model = Monotub
        fields = '__all__'
