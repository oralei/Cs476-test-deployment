from django.core.management.commands.migrate import Command as MigrateCommand
from django.contrib.auth.management import create_permissions
from django.db.models.signals import post_migrate

class Command(MigrateCommand):
    help = 'Run migrations without automatic permission creation (MongoDB compatibility fix)'
    
    def handle(self, *args, **options):
        # Disconnect the problematic signal
        post_migrate.disconnect(
            create_permissions,
            dispatch_uid="django.contrib.auth.management.create_permissions"
        )
        
        # Run the normal migrate command
        result = super().handle(*args, **options)
        
        self.stdout.write(self.style.SUCCESS('\nMigrations completed (permissions creation disabled for MongoDB compatibility)'))
        
        return result