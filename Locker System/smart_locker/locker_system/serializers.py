from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Locker, Reservation
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

# --------------------------
# User Serializer (Register)
# --------------------------
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    role = serializers.ChoiceField(choices=[('user','User'), ('admin','Admin')], default='user')

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

# --------------------------
# JWT Login Serializer
# --------------------------
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        from django.contrib.auth import authenticate
        user = authenticate(**data)
        if user and user.is_active:
            refresh = RefreshToken.for_user(user)
            return {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'role': user.role
            }
        raise serializers.ValidationError("Invalid credentials")

# --------------------------
# Locker Serializer
# --------------------------
class LockerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Locker
        fields = '__all__'

# --------------------------
# Reservation Serializer
# --------------------------
class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = '__all__'
        read_only_fields = ('user',)

# --------------------------
# Locker Serializer
# --------------------------
class LockerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Locker
        fields = ['id', 'locker_number', 'location', 'status', 'is_occupied']

# --------------------------
# Reservation Serializer
# --------------------------
class ReservationSerializer(serializers.ModelSerializer):
    locker = LockerSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Reservation
        fields = ['id', 'locker', 'user', 'reserved_at', 'released_at']