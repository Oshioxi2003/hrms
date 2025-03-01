from django.apps import AppConfig
from django.db.models.signals import post_migrate

def setup_groups(sender, **kwargs):
    # Call the setup_groups management command after migrations
    from django.core.management import call_command
    call_command('setup_groups')

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        # Connect the post_migrate signal to setup_groups
        post_migrate.connect(setup_groups, sender=self)
