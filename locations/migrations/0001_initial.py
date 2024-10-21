from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('media_type', models.CharField(max_length=20)),
                ('title', models.CharField(max_length=300)),
                ('place_name', models.CharField(max_length=300)),
                ('place_type', models.CharField(max_length=100)),
                ('place_description', models.TextField(max_length=300)),
                ('opening_hours', models.TextField(max_length=300)),
                ('break_time', models.CharField(max_length=100)),
                ('closed_day', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=300)),
                ('latitude', models.FloatField(max_length=8)),
                ('longitude', models.FloatField(max_length=10)),
                ('tel', models.CharField(max_length=20)),
                ('created_at', models.CharField(max_length=10)),
                ('save_count', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='LocationSave',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('saved_at', models.DateTimeField(auto_now_add=True)),
                ('location', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='locations.location')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='location_save', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'location')},
            },
        ),
    ]
