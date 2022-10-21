from rest_framework import mixins, viewsets


class ListRetrieveViewSet(mixins.RetrieveModelMixin,
                          mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    """List and retrieve view set."""
    pass


class ListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """List and retrieve view set."""
    pass
