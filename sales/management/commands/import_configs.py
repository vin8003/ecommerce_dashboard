import json
from django.core.management.base import BaseCommand
from sales.models import Platform


class Command(BaseCommand):
    help = 'Load all existing platform related configs from JSON files'
    config_path = 'sales/management/configs/platform_config.json'

    def handle(self, *args, **kwargs):
        with open(self.config_path, 'r') as f:
            platform_configs = json.load(f)

        for platform_name, platform_config in platform_configs.items():
            Platform.objects.update_or_create(
                platform_name=platform_name,
                defaults={'platform_config': platform_config}
            )

        self.stdout.write('Platform configs loaded successfully.')