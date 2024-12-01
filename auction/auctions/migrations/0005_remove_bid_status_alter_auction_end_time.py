# Generated by Django 5.1.3 on 2024-12-01 09:05

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_alter_auction_end_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bid',
            name='status',
        ),
        migrations.AlterField(
            model_name='auction',
            name='end_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2024, 12, 1, 9, 5, 42, 189428, tzinfo=datetime.timezone.utc), null=True),
        ),
    ]