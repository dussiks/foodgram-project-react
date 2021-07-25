from djoser.views import UserViewSet

from .models import CustomUser
from .permissions import IsOwnerOrAuthenticatedOrCreateOnly
from .serializers import CustomUserSerializer


class CustomUserModelViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsOwnerOrAuthenticatedOrCreateOnly, )
