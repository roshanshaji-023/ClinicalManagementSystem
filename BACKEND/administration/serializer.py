'''
Serializers define how your models will be converted to JSON (and back) for API requests/responses.
Validates data before saving to the database
Controls which fields are exposed to the API
'''
from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import Department,Staff,Doctor,Doctor_additional_info
import re
from datetime import date

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
    Staff serializer including:
    - Department details
    - User details
    - Full validation
    '''

    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    # ----------------------------
    # USER INPUT (WRITE ONLY) ✅ IMPORTANT
    # ----------------------------
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    
    # ----------------------------
    # Department (POST via ID)
    # ----------------------------
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.filter(status='active')
    ) # only allow active departments to be assigned

    department_name = serializers.CharField(
        source='department.dept_name',
        read_only=True
    )

    department_code = serializers.CharField(
        source='department.dept_code',
        read_only=True
    )

     # ----------------------------
    # ROLE (VERY IMPORTANT)
    # ----------------------------
    role = serializers.CharField(write_only=True)
    role_name = serializers.SerializerMethodField(read_only=True)

    # ----------------------------
    # USER DETAILS (READ)
    # ----------------------------
    user_username = serializers.CharField(
        source='user.username',
        read_only=True
    )

    user_email = serializers.EmailField(
        source='user.email',
        read_only=True
    )

    user_first_name = serializers.CharField(
        source='user.first_name',
        read_only=True
    )

    user_last_name = serializers.CharField(
        source='user.last_name',
        read_only=True
    )

    class Meta:
        model = Staff
        fields = '__all__' 
        extra_kwargs = {
    'user': {'required': False}
}
    # ----------------------------
    # CREATE (CORE LOGIC)
    # ----------------------------
    def create(self, validated_data):
        role_name = validated_data.pop('role')

        username = validated_data.pop('username')
        password = validated_data.pop('password')
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        email = validated_data.pop('email')

        # Create user
        user = User.objects.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        user.save()

        # Assign role (GROUP)
        try:
            group = Group.objects.get(name=role_name)
        except Group.DoesNotExist:
            raise serializers.ValidationError({"role": "Invalid role"})

        user.groups.add(group)

        # Create staff
        staff = Staff.objects.create(user=user, **validated_data)

        return staff

    # ----------------------------
    # RETURN ROLE
    # ----------------------------
    def get_role_name(self, obj):
        group = obj.user.groups.first()
        return group.name if group else None
    
    def update(self, instance, validated_data):
    # ----------------------------
    # HANDLE USER UPDATE
    # ----------------------------
        user = instance.user

        user.username = validated_data.get('username', user.username)
        user.email = validated_data.get('email', user.email)
        user.first_name = validated_data.get('first_name', user.first_name)
        user.last_name = validated_data.get('last_name', user.last_name)

        password = validated_data.get('password', None)
        if password:
            user.set_password(password)

        user.save()

        # ----------------------------
        # HANDLE ROLE UPDATE
        # ----------------------------
        role_name = validated_data.get('role', None)
        if role_name:
            try:
                group = Group.objects.get(name=role_name)
                user.groups.clear()
                user.groups.add(group)
            except Group.DoesNotExist:
                raise serializers.ValidationError({"role": "Invalid role"})

        # ----------------------------
        # UPDATE STAFF FIELDS
        # ----------------------------
        instance.department = validated_data.get('department', instance.department)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.date_of_birth = validated_data.get('date_of_birth', instance.date_of_birth)
        instance.blood_group = validated_data.get('blood_group', instance.blood_group)
        instance.status = validated_data.get('status', instance.status)

        instance.save()

        return instance

    # ----------------------------
    # FIELD LEVEL VALIDATION
    # ----------------------------

    def validate_phone_number(self, value):
        if not re.fullmatch(r'\d{10,15}', value):
            raise serializers.ValidationError(
                "Phone number must contain 10 to 15 digits."
            )
        return value

    def validate_department(self, value):
        if value.status != 'active':
            raise serializers.ValidationError(
                "Cannot assign staff to an inactive department."
            )
        return value

    # ----------------------------
    # OBJECT LEVEL VALIDATION
    # ----------------------------

    def validate(self, data):
        dob = data.get('date_of_birth')
        today = date.today()

        if dob > today:
            raise serializers.ValidationError({
                "date_of_birth": "Date of birth cannot be in the future."
            })

        age = today.year - dob.year - (
            (today.month, today.day) < (dob.month, dob.day)
        )

        if age < 18:
            raise serializers.ValidationError({
                "date_of_birth": "Staff must be at least 18 years old."
            })

        return data

class DoctorSerializer(serializers.ModelSerializer):
    '''
    Doctor serializer for API representation and validation.
    '''
    # ----------------------------
    # Department (POST via ID)
    # ----------------------------
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.filter(status='active')
    ) # only allow active departments to be assigned

    department_name = serializers.CharField(
        source='department.dept_name',
        read_only=True
    )

    department_code = serializers.CharField(
        source='department.dept_code',
        read_only=True
    )
    # ----------------------------
    # User Details (GET only)
    # ----------------------------
    first_name = serializers.CharField(
        source='user.first_name',
        read_only=True
    )

    last_name = serializers.CharField(
        source='user.last_name',
        read_only=True
    )

    email = serializers.EmailField(
        source='user.email',
        read_only=True
    )

    username = serializers.CharField(
        source='user.username',
        read_only=True
    )
    class Meta:
        model = Doctor
        fields ='__all__'
        
    # ====================================================
    # FIELD LEVEL VALIDATIONS
    # ====================================================

    def validate_phone_number(self, value):
        '''
        Phone number must contain 10–15 digits only.
        '''
        if not re.fullmatch(r'\d{10,15}', value):
            raise serializers.ValidationError(
                "Phone number must contain 10 to 15 digits."
            )
        return value

    def validate_consultation_fee(self, value):
        '''
        Consultation fee must be positive.
        '''
        if value <= 0:
            raise serializers.ValidationError(
                "Consultation fee must be greater than zero."
            )
        return value

    def validate_experience_years(self, value):
        '''
        Experience cannot be negative.
        '''
        if value < 0:
            raise serializers.ValidationError(
                "Experience years cannot be negative."
            )
        return value

    def validate_department(self, value):
        '''
        Extra safety: ensure department is active.
        '''
        if value.status != 'active':
            raise serializers.ValidationError(
                "Cannot assign doctor to inactive department."
            )
        return value

    # ====================================================
    # OBJECT LEVEL VALIDATION (BUSINESS LOGIC)
    # ====================================================

    def validate(self, data):
        '''
        Validate:
        - DOB not future
        - Age >= 23
        - Experience logical check
        '''

        dob = data.get('date_of_birth')
        experience = data.get('experience_years')

        today = date.today()

        # DOB cannot be future
        if dob > today:
            raise serializers.ValidationError({
                "date_of_birth": "Date of birth cannot be in the future."
            })

        # Accurate age calculation
        age = today.year - dob.year - (
            (today.month, today.day) < (dob.month, dob.day)
        )

        # Doctor must be at least 23
        if age < 23:
            raise serializers.ValidationError({
                "date_of_birth": "Doctor must be at least 23 years old."
            })

        # Experience logical check
        if experience is not None:
            if experience > (age - 22):
                raise serializers.ValidationError({
                    "experience_years": "Experience years exceed logical working age."
                })

        return data

class DoctorAdditionalInfoSerializer(serializers.ModelSerializer):
    '''
    Doctor additional info serializer for API representation and validation.
    '''
    class Meta:
        model = Doctor_additional_info
        fields ='__all__'