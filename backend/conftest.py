from datetime import timedelta
from decimal import Decimal
import itertools

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.events.models import Category, Event
from apps.payments.models import Payment
from apps.tickets.models import TicketType


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_factory(db):
    counter = itertools.count(1)
    user_model = get_user_model()

    def create_user(**kwargs):
        index = next(counter)
        password = kwargs.pop('password', 'StrongPass123!')
        defaults = {
            'email': f'user{index}@example.com',
            'first_name': 'Test',
            'last_name': f'User{index}',
            'role': user_model.Role.ATTENDEE,
        }
        defaults.update(kwargs)
        user = user_model.objects.create_user(password=password, **defaults)
        user.raw_password = password
        return user

    return create_user


@pytest.fixture
def auth_headers_for():
    def make_headers(user):
        token = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {token.access_token}'}

    return make_headers


@pytest.fixture
def event_factory(db, user_factory):
    category_counter = itertools.count(1)
    event_counter = itertools.count(1)

    def create_event(**kwargs):
        organizer = kwargs.pop('organizer', user_factory(role='organizer'))
        category_index = next(category_counter)
        category = kwargs.pop(
            'category',
            Category.objects.create(
                name=f'Category {category_index}',
                slug=f'category-{category_index}',
            ),
        )
        event_index = next(event_counter)
        start_date = kwargs.pop('start_date', timezone.now() + timedelta(days=7))
        end_date = kwargs.pop('end_date', start_date + timedelta(hours=3))
        defaults = {
            'organizer': organizer,
            'category': category,
            'title': f'Event {event_index}',
            'slug': f'event-{event_index}',
            'description': 'Test event description',
            'status': Event.Status.PUBLISHED,
            'event_type': Event.EventType.IN_PERSON,
            'start_date': start_date,
            'end_date': end_date,
            'venue_name': 'Main Hall',
            'city': 'Lagos',
            'country': 'Nigeria',
        }
        defaults.update(kwargs)
        return Event.objects.create(**defaults)

    return create_event


@pytest.fixture
def ticket_type_factory(db):
    def create_ticket_type(event, **kwargs):
        defaults = {
            'event': event,
            'name': 'General Admission',
            'description': 'Access pass',
            'price': Decimal('49.99'),
            'quantity': 50,
            'quantity_sold': 0,
        }
        defaults.update(kwargs)
        return TicketType.objects.create(**defaults)

    return create_ticket_type


@pytest.fixture
def payment_factory(db):
    def create_payment(user, event, **kwargs):
        defaults = {
            'user': user,
            'event': event,
            'amount': Decimal('99.98'),
            'currency': 'USD',
            'status': Payment.Status.PENDING,
            'provider': Payment.Provider.STRIPE,
            'provider_session_id': 'cs_test_default',
            'metadata': {},
        }
        defaults.update(kwargs)
        return Payment.objects.create(**defaults)

    return create_payment
