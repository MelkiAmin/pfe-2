from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import OrganizerProfile
from .serializers import OrganizerProfileSerializer
from utils.permissions import IsOrganizerOrAdmin


class OrganizerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = OrganizerProfileSerializer
    permission_classes = [IsOrganizerOrAdmin]

    def get_object(self):
        profile, _ = OrganizerProfile.objects.get_or_create(user=self.request.user)
        return profile


class OrganizerListView(generics.ListAPIView):
    queryset = OrganizerProfile.objects.filter(is_verified=True).select_related('user')
    serializer_class = OrganizerProfileSerializer
    permission_classes = [permissions.AllowAny]


class OrganizerDashboardView(APIView):
    permission_classes = [IsOrganizerOrAdmin]

    def get(self, request):
        from apps.events.models import Event
        from apps.tickets.models import Ticket

        events = Event.objects.filter(organizer=request.user)
        total_events = events.count()
        published_events = events.filter(status='published').count()
        total_tickets_sold = Ticket.objects.filter(
            event__organizer=request.user, status='confirmed'
        ).count()

        return Response({
            'total_events': total_events,
            'published_events': published_events,
            'total_tickets_sold': total_tickets_sold,
        })