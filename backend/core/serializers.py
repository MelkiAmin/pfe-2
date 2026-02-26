from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from core.models import User
from core.models import Event, Category, Location, GalleryImage, Speaker, TimeSlot, Slot
from core.models import Order
from core.models import Organizer, Transaction, Withdrawal, WithdrawMethod
from core.models import Admin
from core.models import NotificationLog, SupportTicket, SupportMessage, SupportAttachment




# ─── Register ────────────────────────────────────────────────
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name', 'mobile')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            mobile=validated_data.get('mobile', ''),
        )
        return user


# ─── Login ───────────────────────────────────────────────────
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


# ─── User Profile ─────────────────────────────────────────────
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'mobile', 'country_name', 'city', 'address',
            'balance', 'profile_complete', 'ev', 'ts',
            'created_at',
        )
        read_only_fields = ('id', 'balance', 'created_at')


# ─── Change Password ──────────────────────────────────────────
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Les mots de passe ne correspondent pas."})
        return attrs




# ─── Category ────────────────────────────────────────────────
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'image', 'slug', 'sort_order', 'status')


# ─── Location ────────────────────────────────────────────────
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'name', 'slug', 'image', 'is_featured', 'sort_order', 'status')


# ─── Gallery Image ───────────────────────────────────────────
class GalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryImage
        fields = ('id', 'image')


# ─── Speaker ─────────────────────────────────────────────────
class SpeakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speaker
        fields = ('id', 'name', 'designation', 'social', 'image')


# ─── Slot ────────────────────────────────────────────────────
class SlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slot
        fields = ('id', 'start_time', 'end_time', 'title', 'description')


# ─── TimeSlot ────────────────────────────────────────────────
class TimeSlotSerializer(serializers.ModelSerializer):
    slots = SlotSerializer(many=True, read_only=True, source='slot_set')

    class Meta:
        model = TimeSlot
        fields = ('id', 'date', 'slots')


# ─── Event List (résumé) ─────────────────────────────────────
class EventListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(source='category_id_obj', read_only=True)
    location = LocationSerializer(source='location_id_obj', read_only=True)

    class Meta:
        model = Event
        fields = (
            'id', 'title', 'slug', 'cover_image', 'short_description',
            'start_date', 'end_date', 'price', 'seats', 'seats_booked',
            'type', 'is_featured', 'status', 'category', 'location',
            'location_address', 'created_at',
        )


# ─── Event Detail (complet) ──────────────────────────────────
class EventDetailSerializer(serializers.ModelSerializer):
    gallery_images = GalleryImageSerializer(many=True, read_only=True, source='galleryimage_set')
    speakers = SpeakerSerializer(many=True, read_only=True, source='speaker_set')
    time_slots = TimeSlotSerializer(many=True, read_only=True, source='timeslot_set')

    class Meta:
        model = Event
        fields = (
            'id', 'title', 'slug', 'cover_image', 'short_description',
            'description', 'start_date', 'end_date', 'price', 'seats',
            'seats_booked', 'type', 'is_featured', 'status', 'link',
            'location_address', 'verification_details',
            'organizer_id', 'category_id', 'location_id',
            'gallery_images', 'speakers', 'time_slots', 'created_at',
        )


# ─── Event Create/Update ─────────────────────────────────────
class EventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = (
            'title', 'slug', 'cover_image', 'short_description', 'description',
            'start_date', 'end_date', 'price', 'seats', 'type', 'link',
            'location_address', 'category_id', 'location_id',
        )

    def create(self, validated_data):
        # L'organisateur_id sera défini dans la vue
        return Event.objects.create(**validated_data)





# ─── Order ───────────────────────────────────────────────────
class OrderSerializer(serializers.ModelSerializer):
    event = EventListSerializer(source='event_id_obj', read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'event_id', 'event', 'quantity', 'price',
            'total_price', 'payment_status', 'status',
            'details', 'created_at',
        )
        read_only_fields = ('id', 'price', 'total_price', 'payment_status', 'created_at')


# ─── Order Create ─────────────────────────────────────────────
class OrderCreateSerializer(serializers.Serializer):
    event_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(required=True, min_value=1)

    def validate(self, attrs):
        try:
            event = Event.objects.get(pk=attrs['event_id'], status=True)
        except Event.DoesNotExist:
            raise serializers.ValidationError({'event_id': 'Événement non trouvé.'})

        seats_disponibles = event.seats - event.seats_booked
        if attrs['quantity'] > seats_disponibles:
            raise serializers.ValidationError({
                'quantity': f'Seulement {seats_disponibles} place(s) disponible(s).'
            })

        attrs['event'] = event
        return attrs




# ─── Organizer Register ───────────────────────────────────────
class OrganizerRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Organizer
        fields = (
            'username', 'email', 'password', 'password2',
            'firstname', 'lastname', 'mobile', 'organization_name',
            'title', 'short_description', 'long_description',
        )

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        if Organizer.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "Cet email est déjà utilisé."})
        if Organizer.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({"username": "Ce username est déjà utilisé."})
        return attrs

    def create(self, validated_data):
        import bcrypt
        validated_data.pop('password2')
        password = validated_data.pop('password')
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        organizer = Organizer.objects.create(
            **validated_data,
            password=hashed,
            profile_image='',
            cover_image='',
        )
        return organizer


# ─── Organizer Login ──────────────────────────────────────────
class OrganizerLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


# ─── Organizer Profile ────────────────────────────────────────
class OrganizerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organizer
        fields = (
            'id', 'username', 'email', 'firstname', 'lastname',
            'organization_name', 'title', 'mobile', 'city', 'country_name',
            'short_description', 'long_description', 'profile_image',
            'cover_image', 'balance', 'is_featured', 'profile_complete',
            'created_at',
        )
        read_only_fields = ('id', 'balance', 'created_at')


# ─── Transaction ─────────────────────────────────────────────
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = (
            'id', 'amount', 'charge', 'post_balance',
            'trx_type', 'trx', 'details', 'remark', 'created_at',
        )


# ─── Withdraw Method ─────────────────────────────────────────
class WithdrawMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawMethod
        fields = (
            'id', 'name', 'image', 'min_limit', 'max_limit',
            'fixed_charge', 'percent_charge', 'currency',
        )


# ─── Withdrawal ──────────────────────────────────────────────
class WithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal
        fields = (
            'id', 'amount', 'currency', 'charge', 'final_amount',
            'after_charge', 'status', 'admin_feedback', 'created_at',
        )


# ─── Withdrawal Create ────────────────────────────────────────
class WithdrawalCreateSerializer(serializers.Serializer):
    method_id = serializers.IntegerField(required=True)
    amount = serializers.DecimalField(max_digits=28, decimal_places=2, required=True)

    def validate(self, attrs):
        try:
            method = WithdrawMethod.objects.get(pk=attrs['method_id'], status=True)
        except WithdrawMethod.DoesNotExist:
            raise serializers.ValidationError({'method_id': 'Méthode de retrait non trouvée.'})

        if attrs['amount'] < method.min_limit:
            raise serializers.ValidationError({'amount': f'Montant minimum: {method.min_limit}'})
        if attrs['amount'] > method.max_limit:
            raise serializers.ValidationError({'amount': f'Montant maximum: {method.max_limit}'})

        attrs['method'] = method
        return attrs





# ─── Admin Login ──────────────────────────────────────────────
class AdminLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


# ─── Admin User Management ────────────────────────────────────
class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'mobile', 'balance', 'is_active', 'ev', 'kv',
            'ban_reason', 'created_at',
        )
        read_only_fields = ('id', 'created_at')


# ─── Admin Organizer Management ───────────────────────────────
class AdminOrganizerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organizer
        fields = (
            'id', 'username', 'email', 'firstname', 'lastname',
            'organization_name', 'balance', 'status', 'is_featured',
            'ban_reason', 'created_at',
        )
        read_only_fields = ('id', 'created_at')


# ─── Admin Event Management ───────────────────────────────────
class AdminEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = (
            'id', 'title', 'slug', 'organizer_id', 'category_id',
            'start_date', 'end_date', 'price', 'seats', 'seats_booked',
            'status', 'step', 'is_featured', 'verification_details',
            'cover_image', 'created_at',
        )


# ─── Admin Withdrawal Management ─────────────────────────────
class AdminWithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal
        fields = (
            'id', 'organizer_id', 'amount', 'currency', 'charge',
            'final_amount', 'status', 'admin_feedback', 'created_at',
        )





# ─── Notification ─────────────────────────────────────────────
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationLog
        fields = (
            'id', 'sender', 'sent_from', 'sent_to', 'subject',
            'message', 'notification_type', 'image', 'user_read', 'created_at',
        )


# ─── Support Attachment ───────────────────────────────────────
class SupportAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportAttachment
        fields = ('id', 'attachment')


# ─── Support Message ──────────────────────────────────────────
class SupportMessageSerializer(serializers.ModelSerializer):
    attachments = SupportAttachmentSerializer(many=True, read_only=True, source='supportattachment_set')

    class Meta:
        model = SupportMessage
        fields = ('id', 'admin_id', 'message', 'attachments', 'created_at')


# ─── Support Ticket List ──────────────────────────────────────
class SupportTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTicket
        fields = (
            'id', 'ticket', 'subject', 'status', 'priority',
            'name', 'email', 'last_reply', 'created_at',
        )


# ─── Support Ticket Detail ────────────────────────────────────
class SupportTicketDetailSerializer(serializers.ModelSerializer):
    messages = SupportMessageSerializer(many=True, read_only=True, source='supportmessage_set')

    class Meta:
        model = SupportTicket
        fields = (
            'id', 'ticket', 'subject', 'status', 'priority',
            'name', 'email', 'last_reply', 'messages', 'created_at',
        )


# ─── Support Ticket Create ────────────────────────────────────
class SupportTicketCreateSerializer(serializers.Serializer):
    subject = serializers.CharField(required=True, max_length=255)
    message = serializers.CharField(required=True)
    priority = serializers.ChoiceField(choices=[(1, 'Low'), (2, 'Medium'), (3, 'High')], default=1)


# ─── Support Message Create ───────────────────────────────────
class SupportMessageCreateSerializer(serializers.Serializer):
    message = serializers.CharField(required=True)