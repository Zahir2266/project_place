import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from .models import Location, Event

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser('admin', 'admin@test.com', 'password')

@pytest.mark.django_db
def test_anonymous_user_cannot_create_location(api_client):
    """Проверка: аноним не может создавать локации"""
    response = api_client.post('/api/locations/', {'name': 'Test'})
    assert response.status_code == 403

@pytest.mark.django_db
def test_only_published_events_visible_to_anon(api_client, admin_user):
    """Проверка: обычный юзер не видит черновики"""
    loc = Location.objects.create(name="Loc", lat=0, lon=0)
    Event.objects.create(title="Draft", author=admin_user, location=loc, status='draft', 
                         start_date="2026-01-01T00:00:00Z", end_date="2026-01-01T01:00:00Z")
    Event.objects.create(title="Pub", author=admin_user, location=loc, status='published', 
                         start_date="2026-01-01T00:00:00Z", end_date="2026-01-01T01:00:00Z")
    
    response = api_client.get('/api/events/')
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['title'] == "Pub"