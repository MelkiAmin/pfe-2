from rest_framework import serializers
from .models import Event, Category
from apps.accounts.serializers import UserProfileSerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon']


class EventListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    organizer_name = serializers.CharField(source='organizer.full_name', read_only=True)
    tickets_sold = serializers.ReadOnlyField()
    is_sold_out = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'slug', 'cover_image', 'event_type', 'status',
            'category', 'organizer_name', 'start_date', 'end_date',
            'city', 'country', 'is_free', 'tickets_sold', 'is_sold_out',
        ]


class EventDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    organizer = UserProfileSerializer(read_only=True)
    tickets_sold = serializers.ReadOnlyField()
    is_sold_out = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = '__all__'


class EventCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        exclude = ['organizer', 'slug', 'created_at', 'updated_at']

    def create(self, validated_data):
        from django.utils.text import slugify
        import uuid
        title = validated_data.get('title', '')
        validated_data['slug'] = slugify(title) + '-' + str(uuid.uuid4())[:8]
        validated_data['organizer'] = self.context['request'].user
        return super().create(validated_data)