import uuid

from django.db import models


MEMBER_COLOURS = ['#5B8DB8', '#9B6B9B', '#6BAF8D', '#B8875B']


class Household(models.Model):
    code = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

    def next_colour(self):
        used = set(self.members.values_list('colour', flat=True))
        for c in MEMBER_COLOURS:
            if c not in used:
                return c
        return MEMBER_COLOURS[self.members.count() % len(MEMBER_COLOURS)]


class Member(models.Model):
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='members')
    name = models.CharField(max_length=40)
    colour = models.CharField(max_length=7)
    api_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} ({self.household.code})'


class Entry(models.Model):
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='entries')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='entries')
    date = models.DateField()
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    note = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('household', 'member', 'date')
        ordering = ['-date', 'member__name']

    def __str__(self):
        return f'{self.member.name} {self.date} £{self.amount}'
