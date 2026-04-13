from rest_framework import viewsets, permissions, filters, mixins
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from .models import Event, Category, Favorite, EventReview
from .serializers import (
    EventListSerializer, EventDetailSerializer,
    EventCreateUpdateSerializer, CategorySerializer,
    FavoriteSerializer, EventReviewSerializer,
)
from utils.permissions import IsOrganizerOrAdmin, IsOwnerOrAdmin

@extend_schema_view(
    list=extend_schema(tags=['Events'], summary='List categories'),
    retrieve=extend_schema(tags=['Events'], summary='Retrieve a category'),
    create=extend_schema(tags=['Events'], summary='Create a category'),
    update=extend_schema(tags=['Events'], summary='Replace a category'),
    partial_update=extend_schema(tags=['Events'], summary='Update a category'),
    destroy=extend_schema(tags=['Events'], summary='Delete a category'),
)
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsOrganizerOrAdmin()]

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.select_related('organizer', 'category').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'event_type', 'category', 'city', 'is_free']
    search_fields = ['title', 'description', 'city', 'venue_name']
    ordering_fields = ['start_date', 'created_at', 'title']

    def get_serializer_class(self):
        if self.action == 'list':
            return EventListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return EventCreateUpdateSerializer
        return EventDetailSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        if self.action == 'create':
            return [IsOrganizerOrAdmin()]
        return [IsOwnerOrAdmin()]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'list':
            if not (self.request.user.is_authenticated and
                    self.request.user.role in ['organizer', 'admin']):
                qs = qs.filter(status='published')
        return qs

@extend_schema_view(
    list=extend_schema(tags=['Events'], summary='List favorites'),
    create=extend_schema(tags=['Events'], summary='Add a favorite'),
    destroy=extend_schema(
        tags=['Events'],
        summary='Remove a favorite',
        parameters=[OpenApiParameter('id', int, OpenApiParameter.PATH)],
    ),
)
class FavoriteViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related('event')

@extend_schema_view(
    list=extend_schema(tags=['Events'], summary='List event reviews'),
    retrieve=extend_schema(tags=['Events'], summary='Retrieve an event review'),
    create=extend_schema(tags=['Events'], summary='Create an event review'),
    update=extend_schema(tags=['Events'], summary='Replace an event review'),
    partial_update=extend_schema(tags=['Events'], summary='Update an event review'),
    destroy=extend_schema(tags=['Events'], summary='Delete an event review'),
)
class EventReviewViewSet(viewsets.ModelViewSet):
    serializer_class = EventReviewSerializer
    queryset = EventReview.objects.select_related('user', 'event').all()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        return [IsOwnerOrAdmin()]
