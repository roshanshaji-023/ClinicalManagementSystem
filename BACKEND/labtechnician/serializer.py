from rest_framework import serializers
from .models import LabTestType

class LabTestTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = LabTestType
        fields = ['Lab_test_id', 'Lab_test_name', 'Lab_test_amount']
        read_only_fields = ['Lab_test_id']

     # Field-level validation
    def validate_test_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError(
                "Test type name must be at least 3 characters long."
            )
        return value

    def validate_test_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Test amount must be greater than 0."
            )
        return value
