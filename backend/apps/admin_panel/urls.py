from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.AdminDashboardView.as_view(), name='admin-dashboard'),
    path('events/<int:pk>/analytics/', views.EventAnalyticsDashboardView.as_view(), name='event-analytics-dashboard'),
    path('events/<int:pk>/analytics/data/', views.EventAnalyticsDataView.as_view(), name='event-analytics-data'),
    path('users/', views.AdminUserListView.as_view(), name='admin-users'),
    path('users/<int:pk>/', views.AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('events/', views.AdminEventListView.as_view(), name='admin-events'),
    path('events/<int:pk>/', views.AdminEventDetailView.as_view(), name='admin-event-detail'),
]
