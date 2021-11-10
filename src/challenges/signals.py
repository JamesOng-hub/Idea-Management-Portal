from django.db.models import signals
from django.db.models.signals import post_save, pre_save, pre_delete
from django.dispatch import receiver
from challenges.models import Challenge
from .tasks import change_state
from datetime import datetime, timedelta
from ideas_portal.settings import celery_tasks
from celery.result import AsyncResult
from django.utils import timezone

#sent to celery when challenge is created/updated
@receiver(post_save, sender=Challenge)
def challenge_post_save(instance, created,**kwargs):
    if created :
        d = instance.idea_submission_deadline
        task_id = change_state.apply_async(eta=datetime(d.year,d.month,d.day) , kwargs={"instance_id":instance.id}).id
        celery_tasks.hmset('tasks', { instance.id : task_id })
        print(celery_tasks.hgetall('tasks'))

@receiver(pre_save, sender=Challenge)
def challenge_pre_save(sender, instance, **kwargs):
    try:
        challenge = sender.objects.get(pk = instance.pk)
    except sender.DoesNotExist:
        pass
    else:
        if (not challenge.idea_submission_deadline == instance.idea_submission_deadline) and instance.is_active:
            print(celery_tasks.hgetall('tasks'))
            d = instance.idea_submission_deadline
            new_eta=datetime(d.year,d.month,d.day)
            #get the task id of old task
            old_id = celery_tasks.hget('tasks' , instance.id)
            #remove the task from scheduler
            if old_id:
                AsyncResult(old_id).revoke(terminate=True)
            #add new task to scheduler with updated deadline
            task_id = change_state.apply_async(eta=new_eta,kwargs={"instance_id":instance.id}).id
            celery_tasks.hmset('tasks', { instance.id : task_id })
            print(celery_tasks.hgetall('tasks'))

@receiver(pre_delete, sender=Challenge)
def challenge_pre_delete(sender, instance, **kwargs):
    try:
        challenge = sender.objects.get(pk = instance.pk)
    except sender.DoesNotExist:
        pass
    else:
        id = celery_tasks.hget('tasks' , instance.id)
        if id:
            AsyncResult(id).revoke(terminate=True)
        celery_tasks.hdel('tasks' , instance.id)
        print(celery_tasks.hgetall('tasks'))
