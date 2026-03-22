import uuid

from django.db import migrations, models


def fill_unique_api_tokens(apps, schema_editor):
    Member = apps.get_model('log', 'Member')
    for member in Member.objects.all():
        member.api_token = uuid.uuid4()
        member.save(update_fields=['api_token'])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('log', '0001_initial'),
    ]

    operations = [
        # Add nullable column without UNIQUE — one default value must not be stamped on every row.
        migrations.AddField(
            model_name='member',
            name='api_token',
            field=models.UUIDField(editable=False, null=True, unique=False),
        ),
        migrations.RunPython(fill_unique_api_tokens, noop_reverse),
        migrations.AlterField(
            model_name='member',
            name='api_token',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
