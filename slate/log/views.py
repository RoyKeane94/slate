import json
from datetime import date

from django.contrib.staticfiles import finders
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from .auth_helper import member_from_token_header
from .household_code import (
    generate_unique_household_code,
    is_valid_household_code,
    normalize_household_code,
)
from .models import Household, Member
from .services import entries_payload_for_month, save_today_entry


def _session_ok(request):
    return request.session.get('household_id') and request.session.get('member_id')


def _resolve_auth(request):
    """
    Returns (household_id, member_id, member_name, member_colour) or None.
    Web: session. iOS: Authorization: Token <member.api_token>.
    """
    if _session_ok(request):
        return (
            request.session['household_id'],
            request.session['member_id'],
            request.session.get('member_name', ''),
            request.session.get('member_colour', ''),
        )
    m = member_from_token_header(request)
    if m is None:
        return None
    return (m.household_id, m.id, m.name, m.colour)


@require_GET
def health(request):
    """Railway / load balancer liveness (no DB hit)."""
    return HttpResponse('ok', content_type='text/plain')


@require_GET
def favicon(request):
    path = finders.find('log/favicon.svg')
    if not path:
        raise Http404()
    with open(path, 'rb') as f:
        return HttpResponse(f.read(), content_type='image/svg+xml')


@require_GET
@ensure_csrf_cookie
def landing(request):
    if _session_ok(request):
        return redirect('/log/')
    return render(request, 'log/landing.html')


@require_POST
def create_household(request):
    data = json.loads(request.body)
    name = data.get('name', '').strip()
    code_raw = data.get('code', '')
    code_raw = code_raw if isinstance(code_raw, str) else ''
    code_raw = normalize_household_code(code_raw)

    if not name:
        return JsonResponse({'error': 'Please add your name'}, status=400)

    if not code_raw:
        try:
            code = generate_unique_household_code(model=Household)
        except RuntimeError:
            return JsonResponse({'error': 'Could not create a code. Try again.'}, status=500)
    else:
        if not is_valid_household_code(code_raw):
            return JsonResponse(
                {'error': 'Invalid code — use the 6-character code shown, or leave it blank.'},
                status=400,
            )
        code = code_raw
        if Household.objects.filter(code=code).exists():
            return JsonResponse(
                {'error': 'That code is already taken. Tap Regenerate or try again.'},
                status=400,
            )

    household = Household.objects.create(code=code)
    colour = household.next_colour()
    member = Member.objects.create(household=household, name=name, colour=colour)

    request.session['household_id'] = household.id
    request.session['member_id'] = member.id
    request.session['member_name'] = member.name
    request.session['member_colour'] = member.colour
    return JsonResponse({
        'success': True,
        'code': code,
        'token': str(member.api_token),
        'member_name': member.name,
        'member_colour': member.colour,
    })


@require_POST
def join_household(request):
    data = json.loads(request.body)
    code = data.get('code', '').strip().lower()
    name = data.get('name', '').strip()
    if not code or not name:
        return JsonResponse({'error': 'Please fill in both fields'}, status=400)

    try:
        household = Household.objects.get(code=code)
    except Household.DoesNotExist:
        return JsonResponse({'error': 'code not found'}, status=400)

    member = Member.objects.filter(household=household, name__iexact=name).first()
    if member is None:
        colour = household.next_colour()
        member = Member.objects.create(household=household, name=name, colour=colour)

    request.session['household_id'] = household.id
    request.session['member_id'] = member.id
    request.session['member_name'] = member.name
    request.session['member_colour'] = member.colour
    return JsonResponse({
        'success': True,
        'household_code': household.code,
        'token': str(member.api_token),
        'member_name': member.name,
        'member_colour': member.colour,
    })


@require_GET
def leave_log(request):
    """End browser session and return to the landing page."""
    request.session.flush()
    return redirect('/')


@require_GET
@ensure_csrf_cookie
def log_view(request):
    if not _session_ok(request):
        return redirect('/')
    today = date.today()
    return render(request, 'log/index.html', {
        'logged_in': True,
        'member_name': request.session['member_name'],
        'member_colour': request.session['member_colour'],
        'month_label': today.strftime('%B %Y'),
    })


@require_POST
def save_entry(request):
    auth = _resolve_auth(request)
    if auth is None:
        return JsonResponse({'error': 'Not logged in'}, status=403)
    household_id, member_id, _, _ = auth

    try:
        data = json.loads(request.body)
        payload = save_today_entry(household_id, member_id, data)
        return JsonResponse(payload)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_GET
def entries_for_month(request, year, month):
    auth = _resolve_auth(request)
    if auth is None:
        return JsonResponse({'error': 'Not logged in'}, status=403)
    household_id, _, member_name, member_colour = auth

    payload = entries_payload_for_month(
        household_id, year, month,
        member_name=member_name,
        member_colour=member_colour,
    )
    return JsonResponse(payload)


def error_404(request, exception):
    return render(request, '404.html', status=404)


def error_500(request):
    return render(request, '500.html', status=500)


def error_403(request, exception=None):
    return render(request, '403.html', status=403)
