# Generated by Django 4.2.4 on 2023-08-05 06:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0006_remove_gameroom_is_active_gameroom_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='gameroom',
            options={'ordering': ['status', 'created_at']},
        ),
        migrations.RemoveField(
            model_name='gameroom',
            name='player1',
        ),
        migrations.RemoveField(
            model_name='gameroom',
            name='player2',
        ),
        migrations.CreateModel(
            name='GameMembers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=25)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='game.gameroom')),
            ],
        ),
    ]