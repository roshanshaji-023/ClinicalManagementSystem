'''
Serializers define how your models will be converted to JSON (and back) for API requests/responses.
Validates data before saving to the database
Controls which fields are exposed to the API
'''
from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import Department,Staff,Doctor,Doctor_additional_info
import re

class GroupSerializer(serializers.ModelSerializer):
    '''
    serializer for Group model. Used for user role management.
    '''
    class Meta:
        model = Group
        fields = ['id', 'name']
        
class UserSerializer(serializers.ModelSerializer):
    '''
    serializer for User model. Handles password hashing and hides password in API responses.
    '''
    password = serializers.CharField(write_only=True)  # hide password in API responses
    
    # Allow assigning groups by ID during creation ->POST/PUT requests
    groups = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        many=True,
        required=False
    )

    # Show group names in GET response
    group_names = serializers.StringRelatedField(
        source='groups',
        many=True,
        read_only=True
    )
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name', 'is_staff', 'is_active',
                    'groups',        # for assigning groups
                    'group_names'    # for viewing group names
                ]

    # 🔹 Username validation
    def validate_username(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("Username must be at least 5 characters long.")
        return value

    # 🔹 Email validation
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value
    
    # Password validations
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")

        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")

        if not re.search(r"[0-9]", value):
            raise serializers.ValidationError("Password must contain at least one number.")

        #  Special character validation added
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise serializers.ValidationError(
                "Password must contain at least one special symbol (!@#$%^&* etc)."
            )

        return value
    
    
    def create(self, validated_data):
        groups = validated_data.pop('groups', [])  # extract groups before creating user
        user = User(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            is_staff=validated_data.get('is_staff', False),
            is_active=validated_data.get('is_active', True)
        )
        user.set_password(validated_data['password'])  # hash the password
        user.save()
        
         # Assign groups after user is saved
        user.groups.set(groups)
        
        return user



class DepartmentSerializer(serializers.ModelSerializer):
    '''
    Department serializer for API representation and validation.
    '''
    class Meta:
        model = Department
        fields ='__all__'
    
    # ✅ Field-level validation for dept_code
    def validate_dept_code(self, value):
        """
        Ensure department code:
        - Is alphanumeric
        - Is uppercase (optional business rule)
        - Has minimum length of 3
        """

        if not value.isalnum():
            raise serializers.ValidationError(
                "Department code must be alphanumeric."
            )

        if len(value) < 3:
            raise serializers.ValidationError(
                "Department code must be at least 3 characters long."
            )

        return value.upper()  # Optional: auto convert to uppercase

    # ✅ Field-level validation for dept_name
    def validate_dept_name(self, value):
        """
        Ensure department name:
        - Contains only letters and spaces
        - Minimum length of 3
        """

        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Department name must be at least 3 characters long."
            )

        if not re.match(r"^[A-Za-z ]+$", value):
            raise serializers.ValidationError(
                "Department name can contain only letters and spaces."
            )

        return value.title()  # Optional: auto format name
        
class StaffSerializer(serializers.ModelSerializer):
    '''
    Staff serializer for API representation and validation.
    '''
    class Meta:
        model = Staff
        fields ='__all__'

class DoctorSerializer(serializers.ModelSerializer):
    '''
    Doctor serializer for API representation and validation.
    '''
    class Meta:
        model = Doctor
        fields ='__all__'

class DoctorAdditionalInfoSerializer(serializers.ModelSerializer):
    '''
    Doctor additional info serializer for API representation and validation.
    '''
    class Meta:
        model = Doctor_additional_info
        fields ='__all__'