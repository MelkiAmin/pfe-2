from rest_framework import generics, filters
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.accounts.serializers import UserProfileSerializer
from apps.events.models import Event
from apps.events.serializers import EventListSerializer, EventDetailSerializer, EventCreateUpdateSerializer
from apps.payments.models import Payment
from utils.permissions import IsAdminUser


class AdminDashboardView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        from apps.tickets.models import Ticket
        return Response({
            'total_users': User.objects.count(),
            'total_organizers': User.objects.filter(role='organizer').count(),
            'total_events': Event.objects.count(),
            'published_events': Event.objects.filter(status='published').count(),
            'total_tickets_sold': Ticket.objects.filter(status='confirmed').count(),
            'total_revenue': sum(
                p.amount for p in Payment.objects.filter(status='completed')
            ),
        })


class AdminUserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['email', 'first_name', 'last_name']
    filterset_fields = ['role', 'is_active']


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdminUser]


class AdminEventListView(generics.ListAPIView):
    queryset = Event.objects.select_related('organizer', 'category').all()
    serializer_class = EventListSerializer
    permission_classes = [IsAdminUser]


class AdminEventDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return EventCreateUpdateSerializer
        return EventDetailSerializer