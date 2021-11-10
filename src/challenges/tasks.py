import logging
from celery import shared_task
from ideas_portal.celery import app
from datetime import datetime
from celery.decorators import task
from ideas_portal.settings import celery_tasks

from challenges.models import Challenge

@shared_task
def change_state(instance_id):
    instance = Challenge.objects.get(pk=instance_id)
    try:
        if instance.idea_submission_deadline <= datetime.today().date():
            instance.state = Challenge.State.ENDED
            instance.save()
            celery_tasks.hdel('tasks', instance.id)
    except instance.DoesNotExist:
        logging.warning("Challenge does not exist anymore")
