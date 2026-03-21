import json
from collections import OrderedDict
from datetime import date
from decimal import Decimal, InvalidOperation

from django.contrib.staticfiles import finders
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from .models import Household, Member, Entry


def _session_ok(request):
    return request.session.get('household_id') and request.session.get('member_id')


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
    code = data.get('code', '').strip().lower()
    name = data.get('name', '').strip()
    if not code or not name:
        return JsonResponse({'error': 'Please fill in both fields'})
    if Household.objects.filter(code=code).exists():
        return JsonResponse({'error': 'Code already taken'})

    household = Household.objects.create(code=code)
    colour = household.next_colour()
    member = Member.objects.create(household=household, name=name, colour=colour)

    request.session['household_id'] = household.id
    request.session['member_id'] = member.id
    request.session['member_name'] = member.name
    request.session['member_colour'] = member.colour
    return JsonResponse({'success': True, 'code': code})


@require_POST
def join_household(request):
    data = json.loads(request.body)
    code = data.get('code', '').strip().lower()
    name = data.get('name', '').strip()
    if not code or not name:
        return JsonResponse({'error': 'Please fill in both fields'})

    try:
        household = Household.objects.get(code=code)
    except Household.DoesNotExist:
        return JsonResponse({'error': 'Code not found'})

    # Same code + same name = resume that member (session expired / new device), not a second account.
    member = Member.objects.filter(household=household, name__iexact=name).first()
    if member is None:
        colour = household.next_colour()
        member = Member.objects.create(household=household, name=name, colour=colour)

    request.session['household_id'] = household.id
    request.session['member_id'] = member.id
    request.session['member_name'] = member.name
    request.session['member_colour'] = member.colour
    return JsonResponse({'success': True})


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
    if not _session_ok(request):
        return JsonResponse({'error': 'Not logged in'}, status=403)

    data = json.loads(request.body)
    raw_amount = data.get('amount', 0)
    try:
        amount = Decimal(str(raw_amount))
    except (InvalidOperation, TypeError):
        return JsonResponse({'error': 'Invalid amount'})
    if amount < 0:
        return JsonResponse({'error': 'Invalid amount'})

    note = data.get('note', '').strip()
    if amount > 0 and not note:
        return JsonResponse({'error': 'Add a short note for what you spent'})
    if amount == 0 and not note:
        note = 'No spend'

    today = date.today()
    entry, _ = Entry.objects.update_or_create(
        household_id=request.session['household_id'],
        member_id=request.session['member_id'],
        date=today,
        defaults={'amount': amount, 'note': note},
    )
    return JsonResponse({
        'success': True,
        'entry': {
            'amount': str(entry.amount),
            'note': entry.note,
            'date': str(entry.date),
        },
    })


WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']


@require_GET
def entries_for_month(request, year, month):
    if not _session_ok(request):
        return JsonResponse({'error': 'Not logged in'}, status=403)

    household_id = request.session['household_id']
    qs = (
        Entry.objects
        .filter(household_id=household_id, date__year=year, date__month=month)
        .select_related('member')
        .order_by('-date', 'member__name')
    )

    grouped = OrderedDict()
    total = Decimal('0.00')
    for e in qs:
        key = str(e.date)
        if key not in grouped:
            grouped[key] = {
                'date': key,
                'day': e.date.day,
                'weekday': WEEKDAYS[e.date.weekday()],
                'items': [],
            }
        grouped[key]['items'].append({
            'note': e.note,
            'amount': str(e.amount),
            'member_name': e.member.name,
            'member_colour': e.member.colour,
        })
        total += e.amount

    return JsonResponse({
        'entries': list(grouped.values()),
        'total': str(total),
        'member_name': request.session.get('member_name', ''),
        'member_colour': request.session.get('member_colour', ''),
    })


def error_404(request, exception):
    return render(request, '404.html', status=404)


def error_500(request):
    return render(request, '500.html', status=500)


def error_403(request, exception=None):
    return render(request, '403.html', status=403)
