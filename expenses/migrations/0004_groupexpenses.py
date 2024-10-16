# Generated by Django 5.0.2 on 2024-10-14 10:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('connections', '0004_rename_connection_id_groupconnections_group_connection_id'),
        ('expenses', '0003_alter_expenses_money_owes_and_more'),
        ('user', '0003_alter_userotp_table_alter_users_table'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupExpenses',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('expense_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('money_owes_in_group', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('distribution_type_in_group', models.CharField(choices=[('percentage', 'PERCENTAGE'), ('equally', 'EQUALLY'), ('unequally', 'UNEQUALLY')], max_length=255, null=True)),
                ('total_money_owes', models.DecimalField(decimal_places=2, max_digits=4)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='this_group', to='connections.groups')),
                ('group_user1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user1_in_group', to='user.users')),
                ('group_user2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user2_in_group', to='user.users')),
            ],
            options={
                'db_table': 'sw_group_expenses',
            },
        ),
    ]
