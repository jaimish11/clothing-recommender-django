# Generated by Django 2.1.7 on 2019-04-19 07:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommender', '0002_auto_20190326_0812'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='gender',
            field=models.CharField(blank=True, max_length=1, null=True),
        ),
    ]
