# Generated by Django 5.1.3 on 2024-12-01 09:15

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_remove_bid_status_alter_auction_end_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='bid',
            name='status',
            field=models.CharField(blank=True, default='active', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='auction',
            name='end_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2024, 12, 1, 9, 15, 48, 454770, tzinfo=datetime.timezone.utc), null=True),
        ),
    ]
