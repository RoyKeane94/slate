"""Resolve Member from Authorization: Token <uuid> (iOS)."""
from django.http import HttpRequest

from .models import Member


def member_from_token_header(request: HttpRequest):
    auth = request.headers.get('Authorization') or request.META.get('HTTP_AUTHORIZATION', '')
    if not auth.startswith('Token '):
        return None
    raw = auth[6:].strip()
    if not raw:
        return None
    try:
        return Member.objects.select_related('household').get(api_token=raw)
    except (Member.DoesNotExist, ValueError):
        return None
