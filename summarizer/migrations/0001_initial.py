# Generated by Django 3.0.6 on 2020-05-15 23:42

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FeedbacksSum',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feedback_ids', models.TextField()),
                ('feedback_all', models.TextField()),
                ('summary', models.TextField()),
                ('insert_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('update_date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
