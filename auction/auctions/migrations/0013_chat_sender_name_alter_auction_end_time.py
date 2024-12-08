# Generated by Django 5.1.3 on 2024-12-08 15:47

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0012_alter_auction_end_time_alter_user_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='sender_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='auction',
            name='end_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2024, 12, 8, 15, 47, 40, 425977, tzinfo=datetime.timezone.utc), null=True),
        ),
    ]