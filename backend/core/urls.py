from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from core.views import (
    # User Auth
    RegisterView, LoginView, LogoutView, ProfileView, ChangePasswordView,
    # Events
    EventListCreateView, EventDetailView, CategoryListView, LocationListView,
    # Orders
    OrderListCreateView, OrderDetailView,
    # Organizer
    OrganizerRegisterView, OrganizerLoginView, OrganizerProfileView,
    OrganizerEventListView, OrganizerEventOrdersView, OrganizerStatsView,
    OrganizerTransactionListView, WithdrawMethodListView, OrganizerWithdrawalView,
    # Admin
    AdminLoginView, AdminStatsView,
    AdminUserListView, AdminUserDetailView, AdminUserBanView,
    AdminEventListView, AdminEventVerifyView,
    AdminOrderListView, AdminTransactionListView,
    AdminWithdrawalListView, AdminWithdrawalProcessView,
    # Notifications
    NotificationListView, NotificationMarkReadView,
    # Support
    SupportTicketListCreateView, SupportTicketDetailView,
    SupportTicketCloseView, AdminSupportTicketListView, AdminSupportTicketReplyView,
)
    from core.views import OrderQRCodeView


urlpatterns = [
    # ── User Auth ──────────────────────────────────────────────
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # ── User ───────────────────────────────────────────────────
    path('user/profile/', ProfileView.as_view(), name='profile'),
    path('user/change-password/', ChangePasswordView.as_view(), name='change_password'),

    # ── Events ─────────────────────────────────────────────────
    path('events/', EventListCreateView.as_view(), name='event_list'),
    path('events/<int:pk>/', EventDetailView.as_view(), name='event_detail'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('locations/', LocationListView.as_view(), name='location_list'),

    # ── Orders ─────────────────────────────────────────────────
    path('orders/', OrderListCreateView.as_view(), name='order_list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('orders/<int:pk>/cancel/', OrderDetailView.as_view(), name='order_cancel'),

    # ── Organizer ──────────────────────────────────────────────
    path('organizer/register/', OrganizerRegisterView.as_view(), name='organizer_register'),
    path('organizer/login/', OrganizerLoginView.as_view(), name='organizer_login'),
    path('organizer/profile/', OrganizerProfileView.as_view(), name='organizer_profile'),
    path('organizer/events/', OrganizerEventListView.as_view(), name='organizer_events'),
    path('organizer/events/<int:event_id>/orders/', OrganizerEventOrdersView.as_view(), name='organizer_event_orders'),
    path('organizer/stats/', OrganizerStatsView.as_view(), name='organizer_stats'),
    path('organizer/transactions/', OrganizerTransactionListView.as_view(), name='organizer_transactions'),
    path('organizer/withdraw-methods/', WithdrawMethodListView.as_view(), name='withdraw_methods'),
    path('organizer/withdrawals/', OrganizerWithdrawalView.as_view(), name='organizer_withdrawals'),

    # ── Admin Auth ─────────────────────────────────────────────
    path('admin/login/', AdminLoginView.as_view(), name='admin_login'),

    # ── Admin Dashboard ────────────────────────────────────────
    path('admin/stats/', AdminStatsView.as_view(), name='admin_stats'),
    path('admin/users/', AdminUserListView.as_view(), name='admin_users'),
    path('admin/users/<int:pk>/', AdminUserDetailView.as_view(), name='admin_user_detail'),
    path('admin/users/<int:pk>/ban/', AdminUserBanView.as_view(), name='admin_user_ban'),
    path('admin/events/', AdminEventListView.as_view(), name='admin_events'),
    path('admin/events/<int:pk>/verify/', AdminEventVerifyView.as_view(), name='admin_event_verify'),
    path('admin/orders/', AdminOrderListView.as_view(), name='admin_orders'),
    path('admin/transactions/', AdminTransactionListView.as_view(), name='admin_transactions'),
    path('admin/withdrawals/', AdminWithdrawalListView.as_view(), name='admin_withdrawals'),
    path('admin/withdrawals/<int:pk>/process/', AdminWithdrawalProcessView.as_view(), name='admin_withdrawal_process'),

    # ── Notifications ──────────────────────────────────────────
    path('notifications/', NotificationListView.as_view(), name='notifications'),
    path('notifications/read-all/', NotificationMarkReadView.as_view(), name='notifications_read_all'),
    path('notifications/<int:pk>/read/', NotificationMarkReadView.as_view(), name='notification_read'),

    # ── Support ────────────────────────────────────────────────
    path('support/', SupportTicketListCreateView.as_view(), name='support_list'),
    path('support/<int:pk>/', SupportTicketDetailView.as_view(), name='support_detail'),
    path('support/<int:pk>/close/', SupportTicketCloseView.as_view(), name='support_close'),
    path('admin/support/', AdminSupportTicketListView.as_view(), name='admin_support'),
    path('admin/support/<int:pk>/reply/', AdminSupportTicketReplyView.as_view(), name='admin_support_reply'),

# Dans urlpatterns ajoutez :
path('orders/<int:pk>/qrcode/', OrderQRCodeView.as_view(), name='order_qrcode'),
]

