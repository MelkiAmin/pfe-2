from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from core.models import User
from core.serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
)

from core.models import Event, Category, Location
from core.serializers import (
    EventListSerializer,
    EventDetailSerializer,
    EventCreateSerializer,
    CategorySerializer,
    LocationSerializer,
)

from core.models import Order
from core.serializers import OrderSerializer, OrderCreateSerializer

from core.models import Organizer, Transaction, Withdrawal, WithdrawMethod
from core.serializers import (
    OrganizerRegisterSerializer,
    OrganizerLoginSerializer,
    OrganizerProfileSerializer,
    TransactionSerializer,
    WithdrawMethodSerializer,
    WithdrawalSerializer,
    WithdrawalCreateSerializer,
)
import bcrypt
import jwt
from django.conf import settings as django_settings

from core.models import Admin
from core.serializers import (
    AdminLoginSerializer,
    AdminUserSerializer,
    AdminOrganizerSerializer,
    AdminEventSerializer,
    AdminWithdrawalSerializer,
)
from django.db.models import Sum, Count

from core.models import NotificationLog, SupportTicket, SupportMessage
from core.serializers import (
    NotificationSerializer,
    SupportTicketSerializer,
    SupportTicketDetailSerializer,
    SupportTicketCreateSerializer,
    SupportMessageCreateSerializer,
)
import uuid

import qrcode
import base64
from io import BytesIO
from core.models import Order

from core.email_service import send_welcome_email, send_order_confirmation



def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# ─── Register ────────────────────────────────────────────────
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens_for_user(user)
            return Response({
                'message': 'Compte créé avec succès.',
                'user': UserProfileSerializer(user).data,
                'tokens': tokens,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


        # Dans RegisterView.post(), après user = serializer.save() :
send_welcome_email(user.email, user.get_full_name() or user.username)

# Dans ConfirmPaymentView.post(), après order.save() :
try:
    from core.models import Event
    event = Event.objects.get(pk=order.event_id)
    send_order_confirmation(
        user_email=request.user.email,
        user_name=request.user.get_full_name() or request.user.username,
        order_id=order.id,
        event_title=event.title,
        quantity=order.quantity,
        total_price=order.total_price,
    )
except Exception:
    pass


# ─── Login ───────────────────────────────────────────────────
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password'],
            )
            if user:
                if not user.is_active:
                    return Response({'error': 'Compte désactivé.'}, status=status.HTTP_403_FORBIDDEN)
                tokens = get_tokens_for_user(user)
                return Response({
                    'message': 'Connexion réussie.',
                    'user': UserProfileSerializer(user).data,
                    'tokens': tokens,
                }, status=status.HTTP_200_OK)
            return Response({'error': 'Identifiants incorrects.'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── Logout ──────────────────────────────────────────────────
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Déconnexion réussie.'}, status=status.HTTP_200_OK)
        except Exception:
            return Response({'error': 'Token invalide.'}, status=status.HTTP_400_BAD_REQUEST)


# ─── Profile ─────────────────────────────────────────────────
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Profil mis à jour.',
                'user': serializer.data,
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── Change Password ─────────────────────────────────────────
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({'error': 'Ancien mot de passe incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Mot de passe modifié avec succès.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)







# ─── Liste & Création des événements ─────────────────────────
class EventListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request):
        events = Event.objects.filter(status=True)

        # Filtres
        category = request.query_params.get('category')
        location = request.query_params.get('location')
        search = request.query_params.get('search')
        featured = request.query_params.get('featured')

        if category:
            events = events.filter(category_id=category)
        if location:
            events = events.filter(location_id=location)
        if search:
            events = events.filter(title__icontains=search)
        if featured:
            events = events.filter(is_featured=True)

        serializer = EventListSerializer(events, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EventCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(organizer_id=request.user.id)
            return Response({
                'message': 'Événement créé avec succès.',
                'event': serializer.data,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── Détail, Modification, Suppression ───────────────────────
class EventDetailView(APIView):
    def get_permissions(self):
        if self.request.method in ['PUT', 'DELETE']:
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_object(self, pk):
        try:
            return Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            return None

    def get(self, request, pk):
        event = self.get_object(pk)
        if not event:
            return Response({'error': 'Événement non trouvé.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = EventDetailSerializer(event)
        return Response(serializer.data)

    def put(self, request, pk):
        event = self.get_object(pk)
        if not event:
            return Response({'error': 'Événement non trouvé.'}, status=status.HTTP_404_NOT_FOUND)
        if event.organizer_id != request.user.id:
            return Response({'error': 'Non autorisé.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = EventCreateSerializer(event, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Événement mis à jour.', 'event': serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        event = self.get_object(pk)
        if not event:
            return Response({'error': 'Événement non trouvé.'}, status=status.HTTP_404_NOT_FOUND)
        if event.organizer_id != request.user.id:
            return Response({'error': 'Non autorisé.'}, status=status.HTTP_403_FORBIDDEN)
        event.delete()
        return Response({'message': 'Événement supprimé.'}, status=status.HTTP_204_NO_CONTENT)


# ─── Catégories ───────────────────────────────────────────────
class CategoryListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        categories = Category.objects.filter(status=True).order_by('sort_order')
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


# ─── Locations ────────────────────────────────────────────────
class LocationListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        locations = Location.objects.filter(status=True).order_by('sort_order')
        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data)




# ─── Liste & Création des commandes ──────────────────────────
class OrderListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user_id=request.user.id).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        if serializer.is_valid():
            event = serializer.validated_data['event']
            quantity = serializer.validated_data['quantity']
            total_price = event.price * quantity

            # Créer la commande
            order = Order.objects.create(
                event_id=event.id,
                user_id=request.user.id,
                price=event.price,
                quantity=quantity,
                total_price=total_price,
                payment_status=0,  # en attente
                status=True,
            )

            # Réserver les places
            event.seats_booked += quantity
            event.save()

            return Response({
                'message': 'Commande créée avec succès.',
                'order': OrderSerializer(order).data,
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── Détail & Annulation d'une commande ──────────────────────
class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user_id):
        try:
            return Order.objects.get(pk=pk, user_id=user_id)
        except Order.DoesNotExist:
            return None

    def get(self, request, pk):
        order = self.get_object(pk, request.user.id)
        if not order:
            return Response({'error': 'Commande non trouvée.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def put(self, request, pk):
        order = self.get_object(pk, request.user.id)
        if not order:
            return Response({'error': 'Commande non trouvée.'}, status=status.HTTP_404_NOT_FOUND)

        if order.payment_status == 1:
            return Response({'error': 'Impossible d\'annuler une commande déjà payée.'}, status=status.HTTP_400_BAD_REQUEST)

        # Libérer les places
        try:
            event = Event.objects.get(pk=order.event_id)
            event.seats_booked -= order.quantity
            event.save()
        except Event.DoesNotExist:
            pass

        order.status = False
        order.payment_status = 3  # annulé
        order.save()

        return Response({'message': 'Commande annulée avec succès.'})




def get_organizer_token(organizer):
    """Génère un token JWT pour l'organisateur."""
    refresh = RefreshToken()
    refresh['organizer_id'] = organizer.id
    refresh['username'] = organizer.username
    refresh['type'] = 'organizer'
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# ─── Organizer Register ───────────────────────────────────────
class OrganizerRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OrganizerRegisterSerializer(data=request.data)
        if serializer.is_valid():
            organizer = serializer.save()
            tokens = get_organizer_token(organizer)
            return Response({
                'message': 'Compte organisateur créé avec succès.',
                'organizer': OrganizerProfileSerializer(organizer).data,
                'tokens': tokens,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── Organizer Login ──────────────────────────────────────────
class OrganizerLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OrganizerLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            try:
                organizer = Organizer.objects.get(username=username)
                if bcrypt.checkpw(password.encode('utf-8'), organizer.password.encode('utf-8')):
                    if not organizer.status:
                        return Response({'error': 'Compte désactivé.'}, status=status.HTTP_403_FORBIDDEN)
                    tokens = get_organizer_token(organizer)
                    return Response({
                        'message': 'Connexion réussie.',
                        'organizer': OrganizerProfileSerializer(organizer).data,
                        'tokens': tokens,
                    })
                return Response({'error': 'Identifiants incorrects.'}, status=status.HTTP_401_UNAUTHORIZED)
            except Organizer.DoesNotExist:
                return Response({'error': 'Identifiants incorrects.'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── Organizer Profile ────────────────────────────────────────
class OrganizerProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get_organizer(self, request):
        organizer_id = request.auth.get('organizer_id') if request.auth else None
        if not organizer_id:
            return None
        try:
            return Organizer.objects.get(pk=organizer_id)
        except Organizer.DoesNotExist:
            return None

    def get(self, request):
        organizer = self.get_organizer(request)
        if not organizer:
            return Response({'error': 'Non autorisé.'}, status=status.HTTP_403_FORBIDDEN)
        return Response(OrganizerProfileSerializer(organizer).data)

    def put(self, request):
        organizer = self.get_organizer(request)
        if not organizer:
            return Response({'error': 'Non autorisé.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = OrganizerProfileSerializer(organizer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Profil mis à jour.', 'organizer': serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── Organizer Events ─────────────────────────────────────────
class OrganizerEventListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        organizer_id = request.auth.get('organizer_id') if request.auth else None
        if not organizer_id:
            return Response({'error': 'Non autorisé.'}, status=status.HTTP_403_FORBIDDEN)
        events = Event.objects.filter(organizer_id=organizer_id).order_by('-created_at')
        serializer = EventListSerializer(events, many=True)
        return Response(serializer.data)


# ─── Organizer Event Orders ───────────────────────────────────
class OrganizerEventOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, event_id):
        organizer_id = request.auth.get('organizer_id') if request.auth else None
        if not organizer_id:
            return Response({'error': 'Non autorisé.'}, status=status.HTTP_403_FORBIDDEN)
        try:
            event = Event.objects.get(pk=event_id, organizer_id=organizer_id)
        except Event.DoesNotExist:
            return Response({'error': 'Événement non trouvé.'}, status=status.HTTP_404_NOT_FOUND)
        orders = Order.objects.filter(event_id=event.id).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response({
            'event': EventListSerializer(event).data,
            'orders': serializer.data,
            'total_orders': orders.count(),
            'total_revenue': sum(o.total_price for o in orders if o.payment_status == 1),
        })


# ─── Organizer Stats ──────────────────────────────────────────
class OrganizerStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        organizer_id = request.auth.get('organizer_id') if request.auth else None
        if not organizer_id:
            return Response({'error': 'Non autorisé.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            organizer = Organizer.objects.get(pk=organizer_id)
        except Organizer.DoesNotExist:
            return Response({'error': 'Organisateur non trouvé.'}, status=status.HTTP_404_NOT_FOUND)

        events = Event.objects.filter(organizer_id=organizer_id)
        orders = Order.objects.filter(event_id__in=events.values_list('id', flat=True))
        paid_orders = orders.filter(payment_status=1)

        return Response({
            'total_events': events.count(),
            'active_events': events.filter(status=True).count(),
            'total_orders': orders.count(),
            'paid_orders': paid_orders.count(),
            'total_revenue': sum(o.total_price for o in paid_orders),
            'balance': organizer.balance,
        })


# ─── Organizer Transactions ───────────────────────────────────
class OrganizerTransactionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        organizer_id = request.auth.get('organizer_id') if request.auth else None
        if not organizer_id:
            return Response({'error': 'Non autorisé.'}, status=status.HTTP_403_FORBIDDEN)
        transactions = Transaction.objects.filter(organizer_id=organizer_id).order_by('-created_at')
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)


# ─── Withdraw Methods ─────────────────────────────────────────
class WithdrawMethodListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        methods = WithdrawMethod.objects.filter(status=True)
        serializer = WithdrawMethodSerializer(methods, many=True)
        return Response(serializer.data)


# ─── Organizer Withdrawals ────────────────────────────────────
class OrganizerWithdrawalView(APIView):
    permission_classes = [IsAuthenticated]

    def get_organizer(self, request):
        organizer_id = request.auth.get('organizer_id') if request.auth else None
        if not organizer_id:
            return None
        try:
            return Organizer.objects.get(pk=organizer_id)
        except Organizer.DoesNotExist:
            return None

    def get(self, request):
        organizer = self.get_organizer(request)
        if not organizer:
            return Response({'error': 'Non autorisé.'}, status=status.HTTP_403_FORBIDDEN)
        withdrawals = Withdrawal.objects.filter(organizer_id=organizer.id).order_by('-created_at')
        serializer = WithdrawalSerializer(withdrawals, many=True)
        return Response(serializer.data)

    def post(self, request):
        organizer = self.get_organizer(request)
        if not organizer:
            return Response({'error': 'Non autorisé.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = WithdrawalCreateSerializer(data=request.data)
        if serializer.is_valid():
            method = serializer.validated_data['method']
            amount = serializer.validated_data['amount']
            charge = method.fixed_charge + (amount * method.percent_charge / 100)
            final_amount = amount - charge

            if organizer.balance < amount:
                return Response({'error': 'Solde insuffisant.'}, status=status.HTTP_400_BAD_REQUEST)

            withdrawal = Withdrawal.objects.create(
                method_id=method.id,
                user_id=1,
                organizer_id=organizer.id,
                amount=amount,
                currency=method.currency,
                charge=charge,
                final_amount=final_amount,
                after_charge=final_amount,
                status=2,  # pending
            )
            organizer.balance -= amount
            organizer.save()

            return Response({
                'message': 'Demande de retrait soumise avec succès.',
                'withdrawal': WithdrawalSerializer(withdrawal).data,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)







def get_admin_token(admin):
    refresh = RefreshToken()
    refresh['admin_id'] = admin.id
    refresh['username'] = admin.username
    refresh['type'] = 'admin'
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def is_admin(request):
    return request.auth and request.auth.get('type') == 'admin'


# ─── Admin Login ──────────────────────────────────────────────
class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            try:
                admin = Admin.objects.get(username=username)
                if bcrypt.checkpw(password.encode('utf-8'), admin.password.encode('utf-8')):
                    tokens = get_admin_token(admin)
                    return Response({
                        'message': 'Connexion admin réussie.',
                        'admin': {'id': admin.id, 'username': admin.username, 'email': admin.email},
                        'tokens': tokens,
                    })
                return Response({'error': 'Identifiants incorrects.'}, status=status.HTTP_401_UNAUTHORIZED)
            except Admin.DoesNotExist:
                return Response({'error': 'Identifiants incorrects.'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── Admin Stats ──────────────────────────────────────────────
class AdminStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not is_admin(request):
            return Response({'error': 'Accès refusé.'}, status=status.HTTP_403_FORBIDDEN)

        total_revenue = Order.objects.filter(payment_status=1).aggregate(
            total=Sum('total_price'))['total'] or 0

        return Response({
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'total_organizers': Organizer.objects.count(),
            'active_organizers': Organizer.objects.filter(status=True).count(),
            'total_events': Event.objects.count(),
            'active_events': Event.objects.filter(status=True).count(),
            'pending_events': Event.objects.filter(step=0).count(),
            'total_orders': Order.objects.count(),
            'paid_orders': Order.objects.filter(payment_status=1).count(),
            'total_revenue': total_revenue,
            'pending_withdrawals': Withdrawal.objects.filter(status=2).count(),
        })


# ─── Admin User Management ────────────────────────────────────
class AdminUserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not is_admin(request):
            return Response({'error': 'Accès refusé.'}, status=status.HTTP_403_FORBIDDEN)
        users = User.objects.all().order_by('-date_joined')
        serializer = AdminUserSerializer(users, many=True)
        return Response(serializer.data)


class AdminUserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None

    def put(self, request, pk):
        if not is_admin(request):
            return Response({'error': 'Accès refusé.'}, status=status.HTTP_403_FORBIDDEN)
        user = self.get_object(pk)
        if not user:
            return Response({'error': 'Utilisateur non trouvé.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = AdminUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Utilisateur mis à jour.', 'user': serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminUserBanView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        if not is_admin(request):
            return Response({'error': 'Accès refusé.'}, status=status.HTTP_403_FORBIDDEN)
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur non trouvé.'}, status=status.HTTP_404_NOT_FOUND)

        ban_reason = request.data.get('ban_reason', '')
        user.is_active = not user.is_active
        user.ban_reason = '' if user.is_active else ban_reason
        user.save()

        action = 'réactivé' if user.is_active else 'banni'
        return Response({'message': f'Utilisateur {action} avec succès.'})


# ─── Admin Event Management ───────────────────────────────────
class AdminEventListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not is_admin(request):
            return Response({'error': 'Accès refusé.'}, status=status.HTTP_403_FORBIDDEN)
        events = Event.objects.all().order_by('-created_at')
        serializer = AdminEventSerializer(events, many=True)
        return Response(serializer.data)


class AdminEventVerifyView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        if not is_admin(request):
            return Response({'error': 'Accès refusé.'}, status=status.HTTP_403_FORBIDDEN)
        try:
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            return Response({'error': 'Événement non trouvé.'}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get('action')  # 'approve' ou 'reject'
        details = request.data.get('details', '')

        if action == 'approve':
            event.status = True
            event.step = 1
            event.verification_details = details
            event.save()
            return Response({'message': 'Événement approuvé.'})
        elif action == 'reject':
            event.status = False
            event.step = 2
            event.verification_details = details
            event.save()
            return Response({'message': 'Événement rejeté.'})

        return Response({'error': 'Action invalide. Utilisez "approve" ou "reject".'}, status=status.HTTP_400_BAD_REQUEST)


# ─── Admin Orders ─────────────────────────────────────────────
class AdminOrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not is_admin(request):
            return Response({'error': 'Accès refusé.'}, status=status.HTTP_403_FORBIDDEN)
        orders = Order.objects.all().order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


# ─── Admin Transactions ───────────────────────────────────────
class AdminTransactionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not is_admin(request):
            return Response({'error': 'Accès refusé.'}, status=status.HTTP_403_FORBIDDEN)
        transactions = Transaction.objects.all().order_by('-created_at')
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)


# ─── Admin Withdrawals ────────────────────────────────────────
class AdminWithdrawalListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not is_admin(request):
            return Response({'error': 'Accès refusé.'}, status=status.HTTP_403_FORBIDDEN)
        withdrawals = Withdrawal.objects.all().order_by('-created_at')
        serializer = AdminWithdrawalSerializer(withdrawals, many=True)
        return Response(serializer.data)


class AdminWithdrawalProcessView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        if not is_admin(request):
            return Response({'error': 'Accès refusé.'}, status=status.HTTP_403_FORBIDDEN)
        try:
            withdrawal = Withdrawal.objects.get(pk=pk)
        except Withdrawal.DoesNotExist:
            return Response({'error': 'Retrait non trouvé.'}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get('action')  # 'approve' ou 'reject'
        feedback = request.data.get('feedback', '')

        if action == 'approve':
            withdrawal.status = 1  # success
            withdrawal.admin_feedback = feedback
            withdrawal.save()
            return Response({'message': 'Retrait approuvé.'})
        elif action == 'reject':
            # Rembourser l'organisateur
            try:
                organizer = Organizer.objects.get(pk=withdrawal.organizer_id)
                organizer.balance += withdrawal.amount
                organizer.save()
            except Organizer.DoesNotExist:
                pass
            withdrawal.status = 3  # cancel
            withdrawal.admin_feedback = feedback
            withdrawal.save()
            return Response({'message': 'Retrait rejeté et montant remboursé.'})

        return Response({'error': 'Action invalide.'}, status=status.HTTP_400_BAD_REQUEST)





# ─── Notifications ────────────────────────────────────────────
class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = NotificationLog.objects.filter(
            user_id=request.user.id
        ).order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response({
            'notifications': serializer.data,
            'unread_count': notifications.filter(user_read=False).count(),
        })


class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk=None):
        if pk:
            # Marquer une seule notification
            try:
                notif = NotificationLog.objects.get(pk=pk, user_id=request.user.id)
                notif.user_read = True
                notif.save()
                return Response({'message': 'Notification marquée comme lue.'})
            except NotificationLog.DoesNotExist:
                return Response({'error': 'Notification non trouvée.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Marquer toutes comme lues
            NotificationLog.objects.filter(
                user_id=request.user.id,
                user_read=False
            ).update(user_read=True)
            return Response({'message': 'Toutes les notifications marquées comme lues.'})


# ─── Support Tickets ──────────────────────────────────────────
class SupportTicketListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tickets = SupportTicket.objects.filter(
            user_id=request.user.id
        ).order_by('-created_at')
        serializer = SupportTicketSerializer(tickets, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SupportTicketCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Générer un numéro de ticket unique
            ticket_number = str(uuid.uuid4()).replace('-', '').upper()[:8]

            ticket = SupportTicket.objects.create(
                user_id=request.user.id,
                name=request.user.get_full_name() or request.user.username,
                email=request.user.email,
                ticket=ticket_number,
                subject=serializer.validated_data['subject'],
                priority=serializer.validated_data['priority'],
                status=0,  # open
            )

            # Créer le premier message
            SupportMessage.objects.create(
                support_ticket_id=ticket.id,
                admin_id=0,
                message=serializer.validated_data['message'],
            )

            return Response({
                'message': 'Ticket créé avec succès.',
                'ticket': SupportTicketSerializer(ticket).data,
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SupportTicketDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_ticket(self, pk, user_id):
        try:
            return SupportTicket.objects.get(pk=pk, user_id=user_id)
        except SupportTicket.DoesNotExist:
            return None

    def get(self, request, pk):
        ticket = self.get_ticket(pk, request.user.id)
        if not ticket:
            return Response({'error': 'Ticket non trouvé.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = SupportTicketDetailSerializer(ticket)
        return Response(serializer.data)

    def post(self, request, pk):
        # Répondre à un ticket
        ticket = self.get_ticket(pk, request.user.id)
        if not ticket:
            return Response({'error': 'Ticket non trouvé.'}, status=status.HTTP_404_NOT_FOUND)

        if ticket.status == 3:
            return Response({'error': 'Ce ticket est fermé.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SupportMessageCreateSerializer(data=request.data)
        if serializer.is_valid():
            msg = SupportMessage.objects.create(
                support_ticket_id=ticket.id,
                admin_id=0,
                message=serializer.validated_data['message'],
            )
            from django.utils import timezone
            ticket.last_reply = timezone.now()
            ticket.status = 2  # replied
            ticket.save()

            return Response({
                'message': 'Réponse envoyée.',
                'support_message': {
                    'id': msg.id,
                    'message': msg.message,
                    'created_at': msg.created_at,
                }
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SupportTicketCloseView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            ticket = SupportTicket.objects.get(pk=pk, user_id=request.user.id)
        except SupportTicket.DoesNotExist:
            return Response({'error': 'Ticket non trouvé.'}, status=status.HTTP_404_NOT_FOUND)

        ticket.status = 3  # closed
        ticket.save()
        return Response({'message': 'Ticket fermé avec succès.'})


# ─── Admin Support ────────────────────────────────────────────
class AdminSupportTicketListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not is_admin(request):
            return Response({'error': 'Accès refusé.'}, status=status.HTTP_403_FORBIDDEN)
        tickets = SupportTicket.objects.all().order_by('-created_at')
        serializer = SupportTicketSerializer(tickets, many=True)
        return Response(serializer.data)


class AdminSupportTicketReplyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if not is_admin(request):
            return Response({'error': 'Accès refusé.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            ticket = SupportTicket.objects.get(pk=pk)
        except SupportTicket.DoesNotExist:
            return Response({'error': 'Ticket non trouvé.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = SupportMessageCreateSerializer(data=request.data)
        if serializer.is_valid():
            admin_id = request.auth.get('admin_id')
            msg = SupportMessage.objects.create(
                support_ticket_id=ticket.id,
                admin_id=admin_id,
                message=serializer.validated_data['message'],
            )
            from django.utils import timezone
            ticket.last_reply = timezone.now()
            ticket.status = 1  # answered
            ticket.save()

            return Response({
                'message': 'Réponse admin envoyée.',
                'support_message': {
                    'id': msg.id,
                    'message': msg.message,
                    'created_at': msg.created_at,
                }
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


        


# ─── Générer QR Code pour une commande ───────────────────────
class OrderQRCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, user_id=request.user.id)
        except Order.DoesNotExist:
            return Response({'error': 'Commande non trouvée.'}, status=status.HTTP_404_NOT_FOUND)

        if order.payment_status != 1:
            return Response({'error': 'Commande non payée.'}, status=status.HTTP_400_BAD_REQUEST)

        # Données du QR Code
        qr_data = {
            'order_id': order.id,
            'user_id': order.user_id,
            'event_id': order.event_id,
            'quantity': order.quantity,
            'total_price': str(order.total_price),
        }

        # Générer le QR Code
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(str(qr_data))
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')

        # Convertir en base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        return Response({
            'order_id': order.id,
            'qr_code': f'data:image/png;base64,{img_base64}',
            'order_details': {
                'event_id': order.event_id,
                'quantity': order.quantity,
                'total_price': order.total_price,
                'payment_status': order.payment_status,
            }
        })