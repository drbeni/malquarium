from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class MalquariumTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['capa'] = user.profile.service_plan.get_compressed_capabilities()

        return token


class MalquariumTokenObtainPairView(TokenObtainPairView):
    serializer_class = MalquariumTokenObtainPairSerializer
