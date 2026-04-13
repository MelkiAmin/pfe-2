from django.utils import timezone
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema, inline_serializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers

class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['System'],
        summary='Health check',
        description='Returns a lightweight status response for uptime and connectivity checks.',
        responses={
            200: inline_serializer(
                name='HealthCheckResponse',
                fields={
                    'status': serializers.CharField(),
                    'service': serializers.CharField(),
                    'timestamp': serializers.DateTimeField(),
                },
            ),
        },
        examples=[
            OpenApiExample(
                'Healthy response',
                value={
                    'status': 'ok',
                    'service': 'backend',
                    'timestamp': '2026-04-13T16:30:00Z',
                },
                response_only=True,
            ),
        ],
    )
    def get(self, request):
        return Response({
            'status': 'ok',
            'service': 'backend',
            'timestamp': timezone.now().isoformat(),
        })
