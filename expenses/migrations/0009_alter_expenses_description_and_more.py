# Generated by Django 5.0.2 on 2024-10-15 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0008_alter_groupexpenses_total_money_owes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expenses',
            name='description',
            field=models.CharField(default=None, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='groupexpenses',
            name='description',
            field=models.CharField(default=None, max_length=255, null=True),
        ),
    ]
