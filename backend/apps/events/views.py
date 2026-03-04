from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Event, Category
from .serializers import (
    EventListSerializer, EventDetailSerializer,
    EventCreateUpdateSerializer, CategorySerializer
)
from utils.permissions import IsOrganizerOrAdmin, IsOwnerOrAdmin


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