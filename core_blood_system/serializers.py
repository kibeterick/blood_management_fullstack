from rest_framework import serializers
from .models import Donor, BloodBag, BloodRequest

class DonorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donor
        fields = "__all__" # Includes all fields (id, name, blood_type, etc.)

class BloodBagSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodBag
        fields = "__all__"

class BloodRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodRequest
        fields = "__all__"