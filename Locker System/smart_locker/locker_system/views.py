# locker_system/views.py

from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from django.core.cache import cache
from django.utils import timezone

from .models import User, Locker, Reservation
from .serializers import UserSerializer, LockerSerializer, ReservationSerializer

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Locker, Reservation
from .serializers import *


# REGISTER
@api_view(['POST'])
def register_view(request):

    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response({"message":"User registered"})

    return Response(serializer.errors)


# LOGIN
@api_view(['POST'])
def login_view(request):

    username = request.data.get("username")
    password = request.data.get("password")

    try:
        user = User.objects.get(username=username)

        if user.check_password(password):

            refresh = RefreshToken.for_user(user)

            role = "admin" if user.is_staff else "user"

            return Response({
                "access":str(refresh.access_token),
                "refresh":str(refresh),
                "role":role
            })

        return Response({"detail":"Invalid password"})

    except User.DoesNotExist:
        return Response({"detail":"User not found"})


# GET LOCKERS
@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def lockers(request):

    if request.method == "GET":

        lockers = Locker.objects.all()
        serializer = LockerSerializer(lockers,many=True)
        return Response(serializer.data)

    if request.method == "POST":

        serializer = LockerSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Locker created"})

        return Response(serializer.errors)


# AVAILABLE LOCKERS
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_lockers(request):

    lockers = Locker.objects.filter(is_occupied=False)

    serializer = LockerSerializer(lockers,many=True)

    return Response(serializer.data)


# RESERVE LOCKER
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reserve_locker(request):
    locker_id = request.data.get('locker_id')
    try:
        locker = Locker.objects.get(id=locker_id, status='available')
    except Locker.DoesNotExist:
        return Response({'error': 'Locker not available'}, status=400)

    locker.status = 'occupied'
    locker.is_occupied = True
    locker.save()

    reservation = Reservation.objects.create(locker=locker, user=request.user)
    return Response(ReservationSerializer(reservation).data)
# --------------------------
# Frontend Pages
# --------------------------
def home(request):
    return render(request, 'index.html')

def login_page(request):
    return render(request, 'login.html')

def register_page(request):
    return render(request, 'register.html')

def user_page(request):
    return render(request, 'user.html')

def admin_page(request):
    return render(request, 'admin.html')



# --------------------------
# User Registration (API)
# --------------------------
class RegisterUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

# --------------------------
# Locker CRUD (Admin Only)
# --------------------------
class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return bool(request.user and request.user.is_authenticated and getattr(request.user, 'role', None) == 'admin')

class LockerListCreateView(generics.ListCreateAPIView):
    serializer_class = LockerSerializer
    queryset = Locker.objects.all()
    permission_classes = [IsAdminOrReadOnly]

class LockerDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LockerSerializer
    queryset = Locker.objects.all()
    permission_classes = [IsAdminOrReadOnly]

# --------------------------
# Available Lockers (User)
# --------------------------
class AvailableLockersView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Redis cache example
        lockers = cache.get('available_lockers')
        if not lockers:
            lockers_qs = Locker.objects.filter(status='available')
            lockers = LockerSerializer(lockers_qs, many=True).data
            cache.set('available_lockers', lockers, timeout=60)  # 1 min cache
        return Response(lockers)

# --------------------------
# Reserve Locker (User)
# --------------------------
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reserve_locker(request):
    locker_id = request.data.get('locker_id')
    try:
        locker = Locker.objects.get(id=locker_id, status='available')
    except Locker.DoesNotExist:
        return Response({'error': 'Locker not available'}, status=400)

    locker.status = 'occupied'
    locker.save()

    reservation = Reservation.objects.create(locker=locker, user=request.user)
    return Response(ReservationSerializer(reservation).data)

# --------------------------
# User Reservations
# --------------------------
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_reservations(request):
    reservations = Reservation.objects.filter(user=request.user, released_at__isnull=True)
    serializer = ReservationSerializer(reservations, many=True)
    return Response(serializer.data)

# --------------------------
# Release Locker (User)
# --------------------------
@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def release_locker(request, pk):
    try:
        reservation = Reservation.objects.get(id=pk, user=request.user, released_at__isnull=True)
    except Reservation.DoesNotExist:
        return Response({'error': 'Reservation not found'}, status=404)

    reservation.released_at = timezone.now()
    reservation.save()

    locker = reservation.locker
    locker.status = 'available'
    locker.is_occupied = False
    locker.save()

    return Response({'success': 'Locker released'})

from rest_framework import generics
from .serializers import LoginSerializer
from rest_framework.response import Response
from rest_framework import status

class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)