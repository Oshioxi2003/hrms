# Generated by Django 5.1.6 on 2025-03-01 10:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('employees', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RewardsAndDisciplinary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('Reward', 'Reward'), ('Disciplinary', 'Disciplinary')], max_length=15)),
                ('content', models.TextField()),
                ('decision_date', models.DateField()),
                ('decision_number', models.CharField(blank=True, max_length=50, null=True)),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('attached_file', models.FileField(blank=True, null=True, upload_to='rewards_documents/')),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('decided_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='decisions_made', to='employees.employee')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.employee')),
            ],
            options={
                'verbose_name_plural': 'Rewards and Disciplinary Records',
            },
        ),
    ]
