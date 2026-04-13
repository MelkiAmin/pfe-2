from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce, TruncDate
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from rest_framework import generics, filters, permissions
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view, inline_serializer

from apps.accounts.models import User
from apps.accounts.serializers import UserProfileSerializer
from apps.events.models import Event
from apps.events.serializers import EventListSerializer, EventDetailSerializer, EventCreateUpdateSerializer
from apps.payments.models import Payment
from apps.tickets.models import Ticket
from utils.permissions import IsAdminUser

admin_dashboard_serializer = inline_serializer(
    name='AdminDashboardResponse',
    fields={
        'total_users': serializers.IntegerField(),
        'total_organizers': serializers.IntegerField(),
        'total_events': serializers.IntegerField(),
        'published_events': serializers.IntegerField(),
        'total_tickets_sold': serializers.IntegerField(),
        'total_revenue': serializers.DecimalField(max_digits=10, decimal_places=2),
    },
)

event_analytics_serializer = inline_serializer(
    name='EventAnalyticsResponse',
    fields={
        'event': inline_serializer(
            name='EventAnalyticsMeta',
            fields={
                'id': serializers.IntegerField(),
                'title': serializers.CharField(),
                'status': serializers.CharField(),
                'start_date': serializers.DateTimeField(),
                'end_date': serializers.DateTimeField(),
            },
        ),
        'summary': inline_serializer(
            name='EventAnalyticsSummary',
            fields={
                'tickets_sold': serializers.IntegerField(),
                'revenue': serializers.DecimalField(max_digits=10, decimal_places=2),
                'users': serializers.IntegerField(),
            },
        ),
        'timeline': inline_serializer(
            name='EventAnalyticsTimeline',
            fields={
                'labels': serializers.ListField(child=serializers.CharField()),
                'tickets_sold': serializers.ListField(child=serializers.IntegerField()),
                'revenue': serializers.ListField(child=serializers.DecimalField(max_digits=10, decimal_places=2)),
                'users': serializers.ListField(child=serializers.IntegerField()),
            },
        ),
        'ticket_types': serializers.ListField(
            child=inline_serializer(
                name='EventAnalyticsTicketType',
                fields={
                    'name': serializers.CharField(),
                    'sold': serializers.IntegerField(),
                    'revenue': serializers.DecimalField(max_digits=10, decimal_places=2),
                },
            ),
        ),
    },
)


def build_event_analytics_payload(event):
    sold_statuses = [Ticket.Status.CONFIRMED, Ticket.Status.USED]
    tickets = event.tickets.filter(status__in=sold_statuses)

    timeline_rows = (
        tickets.annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(
            tickets_sold=Count('id'),
            revenue=Coalesce(Sum('price_paid'), Decimal('0.00')),
            users=Count('attendee', distinct=True),
        )
        .order_by('day')
    )

    ticket_type_rows = (
        tickets.values('ticket_type__name')
        .annotate(
            sold=Count('id'),
            revenue=Coalesce(Sum('price_paid'), Decimal('0.00')),
        )
        .order_by('-sold', 'ticket_type__name')
    )

    labels = [row['day'].isoformat() for row in timeline_rows]
    tickets_sold = [row['tickets_sold'] for row in timeline_rows]
    revenue = [row['revenue'] for row in timeline_rows]
    users = [row['users'] for row in timeline_rows]

    total_revenue = sum((row['revenue'] for row in timeline_rows), Decimal('0.00'))

    return {
        'event': {
            'id': event.id,
            'title': event.title,
            'status': event.status,
            'start_date': event.start_date,
            'end_date': event.end_date,
        },
        'summary': {
            'tickets_sold': tickets.count(),
            'revenue': total_revenue,
            'users': tickets.values('attendee').distinct().count(),
        },
        'timeline': {
            'labels': labels,
            'tickets_sold': tickets_sold,
            'revenue': revenue,
            'users': users,
        },
        'ticket_types': [
            {
                'name': row['ticket_type__name'],
                'sold': row['sold'],
                'revenue': row['revenue'],
            }
            for row in ticket_type_rows
        ],
    }


class EventAnalyticsAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    def dispatch(self, request, *args, **kwargs):
        self.event = get_object_or_404(Event.objects.select_related('organizer'), pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        user = self.request.user
        return bool(
            user.is_authenticated and (
                user.role == 'admin' or self.event.organizer_id == user.id
            )
        )

    def handle_no_permission(self):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden('You do not have permission to view this analytics dashboard.')

class AdminDashboardView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=['Admin Panel'],
        summary='Admin dashboard metrics',
        description='Returns aggregate statistics for users, events, tickets, and revenue.',
        responses={200: admin_dashboard_serializer},
    )
    def get(self, request):
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


class EventAnalyticsDashboardView(EventAnalyticsAccessMixin, TemplateView):
    template_name = 'admin_panel/event_analytics_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.event
        context['analytics_api_url'] = f'/api/admin-panel/events/{self.event.pk}/analytics/data/'
        return context

class AdminUserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['email', 'first_name', 'last_name']
    filterset_fields = ['role', 'is_active']

@extend_schema_view(
    get=extend_schema(
        tags=['Admin Panel'],
        summary='Retrieve an admin-managed user',
    ),
    put=extend_schema(
        tags=['Admin Panel'],
        summary='Replace an admin-managed user',
    ),
    patch=extend_schema(
        tags=['Admin Panel'],
        summary='Update an admin-managed user',
    ),
    delete=extend_schema(
        tags=['Admin Panel'],
        summary='Delete an admin-managed user',
    ),
)
class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdminUser]

class AdminEventListView(generics.ListAPIView):
    queryset = Event.objects.select_related('organizer', 'category').all()
    serializer_class = EventListSerializer
    permission_classes = [IsAdminUser]

@extend_schema_view(
    get=extend_schema(
        tags=['Admin Panel'],
        summary='Retrieve an admin-managed event',
    ),
    put=extend_schema(
        tags=['Admin Panel'],
        summary='Replace an admin-managed event',
    ),
    patch=extend_schema(
        tags=['Admin Panel'],
        summary='Update an admin-managed event',
    ),
    delete=extend_schema(
        tags=['Admin Panel'],
        summary='Delete an admin-managed event',
    ),
)
class AdminEventDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return EventCreateUpdateSerializer
        return EventDetailSerializer


class EventAnalyticsDataView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['Admin Panel'],
        summary='Event analytics data',
        description='Returns ticket sales, revenue, and attendee analytics for a specific event.',
        parameters=[OpenApiParameter('pk', int, OpenApiParameter.PATH, description='Event ID')],
        responses={200: event_analytics_serializer},
    )
    def get(self, request, pk):
        event = get_object_or_404(Event.objects.select_related('organizer'), pk=pk)
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication credentials were not provided.'}, status=401)
        if request.user.role != 'admin' and event.organizer_id != request.user.id:
            return Response({'detail': 'You do not have permission to view this event analytics.'}, status=403)
        return Response(build_event_analytics_payload(event))
