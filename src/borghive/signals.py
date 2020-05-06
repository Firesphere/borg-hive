from django.db.models.signals import post_save
from django.dispatch import receiver
from borghive.models import RepositoryEvent, RepositoryUser
import borghive.tasks
import logging

LOGGER = logging.getLogger(__name__)

@receiver(post_save, sender=RepositoryUser)
def repository_user_created(sender, instance, created, **kwargs):
    LOGGER.debug('repository_user_created: %s, %s, %s, %s', sender, instance, created, kwargs)
    if created:
        borghive.tasks.create_repo_user.delay(instance.id)

@receiver(post_save, sender=RepositoryEvent)
def handle_repository_event(sender, instance, created, **kwargs):
    LOGGER.debug('handle_repository_event: %s, %s, %s, %s', sender, instance, created, kwargs)

    LOGGER.debug(instance.event_type)
    LOGGER.debug(instance.message)

    # shaky: repository updated / archive created
    if created and instance.event_type == 'watcher' and 'Repository updated' in instance.message:
        borghive.tasks.create_repo_statistic.delay(repo_id=instance.repo.id)
