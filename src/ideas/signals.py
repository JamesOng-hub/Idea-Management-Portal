from django.db.models.signals import post_save, pre_delete
from .models import Comment
from django.dispatch import receiver
import django.dispatch
from notifications.signals import notify

signal_comment = django.dispatch.Signal(providing_args=["instance"])


def comment_notification(sender, instance, **kwargs):
    form = instance
    idea = form.instance.idea
    recipient = idea.author.user
    verb = 'commented on your idea "{0}"'.format(idea.title)
    notify.send(
        form.instance.user,
        recipient=recipient,
        verb=verb,
        description=form.instance.content
    )


signal_comment.connect(comment_notification)


signal_idea = django.dispatch.Signal(providing_args=["instance"])


def idea_notification(sender, instance, **kwargs):
    form = instance
    idea = form.instance
    author = idea.author
    challenge = idea.challenge
    if not challenge == None:
        recipient = challenge.author
        verb = 'submitted an idea to your challenge "{0}"'.format(
            challenge.title)
        notify.send(
            author,
            recipient=recipient,
            verb=verb,
            description=form.instance.title
        )


signal_idea.connect(idea_notification)


signal_vote = django.dispatch.Signal(providing_args=["instance", "voter"])


def vote_notification(sender, instance, voter, **kwargs):
    idea = instance
    recipient = idea.author.user
    verb = 'voted your idea "{0}"'.format(idea.title)
    notify.send(
        voter,
        recipient=recipient,
        verb=verb,
        description=""
    )


signal_vote.connect(vote_notification)
