'''
Serializers define how your models will be converted to JSON (and back) for API requests/responses.
Validates data before saving to the database
Controls which fields are exposed to the API
'''
from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import Department,Staff,Doctor,Doctor_additional_info

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
    
    # Allow assigning groups by ID during creation
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