from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('history', views.PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
    path('checkout/', views.CreateCheckoutSessionView.as_view(), name='create-checkout'),
    path('webhook/stripe/', views.StripeWebhookView.as_view(), name='stripe-webhook'),
]