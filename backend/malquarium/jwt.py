from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


class MalquariumTokenObtainPairSerializer(TokenObtainPairSerializer):
    swagger_schema = None

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['capa'] = user.profile.service_plan.get_compressed_capabilities()

        return token


class MalquariumTokenObtainPairView(TokenObtainPairView):
    swagger_schema = None
    serializer_class = MalquariumTokenObtainPairSerializer


class MalquariumTokenRefreshView(TokenRefreshView):
    swagger_schema = None
