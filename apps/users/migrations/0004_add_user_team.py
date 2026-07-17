# apps/users/migrations/0004_add_user_team.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_user_is_default_password_user_last_password_change'),
    ]

    operations = [
        # Create UserTeam model
        migrations.CreateModel(
            name='UserTeam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(
                    choices=[
                        ('TEAM_LEAD', 'Team Lead'),
                        ('AGENT', 'Agent'),
                        ('SUPPORT', 'Support'),
                        ('VIEWER', 'Viewer')
                    ],
                    default='AGENT',
                    help_text='Role of the user within this team',
                    max_length=20
                )),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(
                    default=True,
                    help_text='Whether this membership is still active'
                )),
                ('team', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='user_memberships',
                    to='users.team'
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='team_memberships',
                    to='users.user'
                )),
            ],
            options={
                'verbose_name': 'User Team',
                'verbose_name_plural': 'User Teams',
                'ordering': ['-joined_at'],
                'unique_together': {('user', 'team')},
            },
        ),
    ]