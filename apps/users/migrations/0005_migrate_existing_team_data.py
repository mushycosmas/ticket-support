from django.db import migrations


def migrate_user_teams(apps, schema_editor):
    """
    Migrate existing users with team_id to the new UserTeam model.
    """
    User = apps.get_model('users', 'User')
    UserTeam = apps.get_model('users', 'UserTeam')
    
    print("\n" + "="*60)
    print("🔄 STARTING TEAM MIGRATION")
    print("="*60)
    
    # Get all users with a team assigned
    users_with_teams = User.objects.filter(team__isnull=False)
    total = users_with_teams.count()
    
    if total == 0:
        print("ℹ️ No users with teams to migrate.")
        return
    
    print(f"📊 Found {total} users with teams to migrate.")
    print("-"*60)
    
    migrated_count = 0
    skipped_count = 0
    
    for user in users_with_teams:
        # Check if this membership already exists
        exists = UserTeam.objects.filter(
            user=user,
            team=user.team,
            is_active=True
        ).exists()
        
        if not exists:
            # Determine role based on user's global role
            role = 'AGENT'
            
            # Check if user has global TEAM_LEAD role
            if user.role and user.role.name:
                if user.role.name.upper() == 'TEAM_LEAD':
                    role = 'TEAM_LEAD'
            
            # If user is the lead of the team (legacy)
            if user.team.lead_id == user.id:
                role = 'TEAM_LEAD'
            
            # Create UserTeam entry
            UserTeam.objects.create(
                user=user,
                team=user.team,
                role=role,
                is_active=True
            )
            migrated_count += 1
            print(f"✅ {user.username:20} -> {user.team.name:20} ({role})")
        else:
            skipped_count += 1
            print(f"⏭️ {user.username:20} -> already in {user.team.name}")
    
    print("-"*60)
    print(f"📊 Migration Summary:")
    print(f"   ✅ Migrated: {migrated_count} users")
    print(f"   ⏭️ Skipped:  {skipped_count} users")
    print(f"   📝 Total:    {total} users processed")
    print("="*60)
    print("✅ MIGRATION COMPLETE")
    print("="*60)


def reverse_migrate_user_teams(apps, schema_editor):
    """
    Reverse migration - clear UserTeam data.
    """
    UserTeam = apps.get_model('users', 'UserTeam')
    count = UserTeam.objects.count()
    UserTeam.objects.all().delete()
    print(f"\n✅ Reversed migration - Deleted {count} UserTeam records.")


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_add_user_team'),
    ]

    operations = [
        migrations.RunPython(migrate_user_teams, reverse_migrate_user_teams),
    ]