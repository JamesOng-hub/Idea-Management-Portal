# Generated by Django 3.1.3 on 2021-03-14 16:06

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('occupation', models.CharField(blank=True, max_length=255)),
                ('location', models.CharField(blank=True, max_length=255)),
                ('image', models.ImageField(default='default.jpg', upload_to='profile_pics')),
                ('bio', models.CharField(blank=True, max_length=255)),
                ('score', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
