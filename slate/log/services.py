"""Shared entry logic for web (session) and iOS (Token header)."""
from collections import OrderedDict
from datetime import date
from decimal import Decimal, InvalidOperation

from .models import Entry

WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']


def entries_payload_for_month(household_id, year, month, member_name='', member_colour=''):
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

    return {
        'entries': list(grouped.values()),
        'total': str(total),
        'member_name': member_name,
        'member_colour': member_colour,
    }


def save_today_entry(household_id, member_id, data: dict):
    raw_amount = data.get('amount', 0)
    try:
        amount = Decimal(str(raw_amount))
    except (InvalidOperation, TypeError):
        raise ValueError('Invalid amount')
    if amount < 0:
        raise ValueError('Invalid amount')

    note = data.get('note', '').strip()
    if amount > 0 and not note:
        raise ValueError('Add a short note for what you spent')
    if amount == 0 and not note:
        note = 'No spend'

    today = date.today()
    entry, _ = Entry.objects.update_or_create(
        household_id=household_id,
        member_id=member_id,
        date=today,
        defaults={'amount': amount, 'note': note},
    )
    return {
        'success': True,
        'entry': {
            'amount': str(entry.amount),
            'note': entry.note,
            'date': str(entry.date),
        },
    }
