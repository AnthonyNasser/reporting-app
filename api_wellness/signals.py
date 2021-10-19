import errno
import glob
import os

from django.conf import settings
from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.text import slugify

from .constants import CACHE_KEY_ETAG_LATEST_EVENTS
from .models import Event, Profile
from .utils import generate_cache_key


@receiver(post_delete, sender=Profile)
@receiver(post_delete, sender=Event)
def cleanup_orphaned_files(sender, **kwargs):
    """
    Cleans up any orphaned files related to profiles or events
    """
    instance = kwargs.get('instance', None)
    
    if instance is not None:
        files = []
        if sender == Profile:
            # Delete current avatar image
            if instance.avatar:
                instance.avatar.delete()
            # Get any other orphaned avatar image(s) containing this profile id
            files = glob.glob(os.path.join(
                settings.MEDIA_ROOT, 'avatars/{}-*'.format(instance.id))
            )
        elif sender == Event:
            # Delete current poster image
            if instance.poster:
                instance.poster.delete()
            # Get any other orphaned poster image(s) containing this event name
            files = glob.glob(os.path.join(
                settings.MEDIA_ROOT, 'events/{}-*'.format(slugify(instance.name)))
            )

        # Delete any other orphaned file found
        for file in files:
            try:
                os.remove(file)
            except OSError as e:
                if e.errno != errno.ENOENT: # No such file or directory
                    raise

@receiver(post_save, sender=Event)
def cache_event_change(sender, **kwargs):
    """
    Deletes event_list ETag to signal new or updated events
    """
    # Delete ETag for latest events
    cache.delete(generate_cache_key(CACHE_KEY_ETAG_LATEST_EVENTS))
