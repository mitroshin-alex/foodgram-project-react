from .mixins import ListRetrieveViewSet
from .serializers import TagSerializer
from .permissions import ReadOnly
from recipes.models import Tag


class TagViewSet(ListRetrieveViewSet):
    """Obtain token by username and confirmation code."""
    permission_classes = (ReadOnly,)
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
