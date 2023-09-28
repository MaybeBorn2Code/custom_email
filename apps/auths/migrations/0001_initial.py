# Generated by Django 4.1.3 on 2023-07-04 14:22

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=100, unique=True, verbose_name='почта')),
                ('is_active', models.BooleanField(default=True, verbose_name='активность')),
                ('is_superuser', models.BooleanField(default=True, verbose_name='администратор')),
                ('is_staff', models.BooleanField(default=True, verbose_name='менеджер')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='дата регистрации')),
                ('photo', models.ImageField(upload_to='', verbose_name='photo')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'пользователь',
                'verbose_name_plural': 'пользователи',
                'ordering': ('-id',),
            },
        ),
    ]
