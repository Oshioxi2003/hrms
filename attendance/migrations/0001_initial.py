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
            name='WorkShift',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shift_name', models.CharField(max_length=50)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('salary_coefficient', models.DecimalField(decimal_places=2, default=1.0, max_digits=3)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('status', models.BooleanField(default=True, help_text='1: Active, 0: Inactive')),
            ],
        ),
        migrations.CreateModel(
            name='ShiftAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assignment_date', models.DateField(auto_now_add=True)),
                ('effective_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('Active', 'Active'), ('Ended', 'Ended'), ('Cancelled', 'Cancelled')], default='Active', max_length=10)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.employee')),
                ('shift', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance.workshift')),
            ],
            options={
                'unique_together': {('employee', 'shift', 'effective_date')},
            },
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('work_date', models.DateField()),
                ('time_in', models.TimeField(blank=True, null=True)),
                ('time_out', models.TimeField(blank=True, null=True)),
                ('actual_work_hours', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('overtime_hours', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('notes', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('Present', 'Present'), ('On Leave', 'On Leave'), ('Absent', 'Absent'), ('Holiday', 'Holiday'), ('Business Trip', 'Business Trip')], default='Present', max_length=15)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.employee')),
                ('shift', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='attendance.workshift')),
            ],
            options={
                'unique_together': {('employee', 'work_date')},
            },
        ),
    ]
