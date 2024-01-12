from django.db import transaction, IntegrityError
from django.contrib.auth import authenticate
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from .models import Store, User

from .serializers import UserSerializer, StoreSerializer


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Login user after successful registration
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # Include user data in the response
            response_data = {
                'refresh': str(refresh),
                'access_token': access_token,
                'user_id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        store_name = request.data.get('store_name')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            store = Store.objects.filter(store_name=store_name, user=user).first()

            if store is None:
                raise AuthenticationFailed('User not associated with the specified store')

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            response_data = {
                'refresh': str(refresh),
                'access_token': access_token,
                'user_id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'store_name': store_name
            }

            return Response(response_data)

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Retrieve the user details from the authenticated user
        user = request.user

        # Access user data as needed
        user_data = {
            'user_id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }

        return Response(user_data, status=status.HTTP_200_OK)


@authentication_classes([])
class StoreCreationView(APIView):

    def post(self, request):
        store_name = request.data.get('store_name')
        access_token = request.data.get('access_token')

        # Decode the access token to extract user ID
        try:
            decoded_token = AccessToken(access_token)
            user_id = decoded_token['user_id']

            # Check if the store with the given name already exists
            existing_store = Store.objects.filter(user_id=user_id).first()

            if existing_store:
                return Response({'error': 'User already has a store'}, status=status.HTTP_400_BAD_REQUEST)

            # Create a new store for the user
            new_store = Store.objects.create(store_name=store_name, user_id=user_id)

            # Serialize the new store data for the response
            store_data = StoreSerializer(new_store).data

            return Response({'message': 'Store created successfully', 'store': store_data},
                            status=status.HTTP_201_CREATED)

        except IntegrityError as e:
            # Handle the specific integrity error related to duplicate entries
            if 'Duplicate entry' in str(e):
                return Response({'error': f'Store with name "{store_name}" already exists'},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': f'Error creating store: {e}'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': f'Error decoding token: {e}'}, status=status.HTTP_400_BAD_REQUEST)


class GetAllUsersAPIView(APIView):
    def get(self, request):
        all_users = User.objects.all()
        user_serializer = UserSerializer(all_users, many=True)
        return Response({'status_code': status.HTTP_200_OK, 'users': user_serializer.data}, status=status.HTTP_200_OK)
