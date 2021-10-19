import pytz

from datetime import timedelta
from django.utils import timezone

from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.db.models import Value as V
from django.db.models import F, PositiveIntegerField, Sum
from django.db.models.functions import Coalesce

from api_wellness.constants import CACHE_KEY_ETAG_RANKINGS, CACHE_KEY_RANKINGS
from api_wellness.models import Profile
from api_wellness.utils import generate_cache_key


class Command(BaseCommand):
    help = 'Computes and caches daily rankings for users'
    
    @staticmethod
    def calc_diff(previous_rankings, username, current_rank):
        """
        Calculates the rank difference from previous rankings
        Returns:
            Positive    = + int (e.g. 7)
            Negative    = - int (e.g. -7)
            No Change   = 0
            Not Ranked  = 'NR'
        """
        for ranking in previous_rankings:
            if username == ranking['username']:
                return -1 * (current_rank - ranking['rank'])
        else:
            return 'NR' # Not ranked
    
    def handle(self, *args, **options):
        rankings = []
        # Today in local timezone
        today = timezone.localdate(timezone=pytz.timezone('America/Los_Angeles'))
        yesterday = today - timedelta(days=1)
        
        # Cache keys
        yesterday_cache_key = generate_cache_key(CACHE_KEY_RANKINGS.format(yesterday))
        today_cache_key = generate_cache_key(CACHE_KEY_RANKINGS.format(today))
        
        # Get yesterday's rankings
        prev_rankings = cache.get(yesterday_cache_key)

        if prev_rankings is not None: # Remove yesterday's rankings from the cache
            cache.delete(yesterday_cache_key)

        # Fetch all users and compute their points
        query = ('SELECT p.user_id, CAST(SUM(COALESCE(points, 0)) AS UNSIGNED) AS points '
                'FROM api_wellness_profile AS p '
                'LEFT JOIN (SELECT profile_id, SUM(c.points) AS points '
                           'FROM api_wellness_activitylog AS al '
                           'INNER JOIN api_wellness_category AS c '
                           'ON al.category_id = c.id '
                           'GROUP BY profile_id '
                           'UNION ALL '
                           'SELECT profile_id, SUM(e.points) AS points '
                           'FROM api_wellness_eventlog AS el '
                           'INNER JOIN api_wellness_event AS e '
                           'ON el.event_id = e.id '
                           'GROUP BY profile_id '
                           'UNION ALL '
                           'SELECT profile_id, SUM(b.points) AS points '
                           'FROM api_wellness_userbadge as ub '
                           'INNER JOIN api_wellness_badge AS b '
                           'ON ub.badge_id = b.id '
                           'GROUP BY profile_id) lp '
                'ON lp.profile_id = p.user_id '
                'INNER JOIN auth_user as u '
                'ON p.user_id = u.id '
                'GROUP BY p.user_id '
                'ORDER BY points DESC'
        )
        
        profiles = Profile.objects.raw(query)

        # BUG: https://code.djangoproject.com/ticket/10060
        # profiles = Profile.objects.select_related('user').prefetch_related('categories', 'events') \
        #             .annotate(points=Sum(Coalesce(F('categories__points'), V(0)) + Coalesce(F('events__points'), V(0)),
        #                                  output_field=PositiveIntegerField(), distinct=True)).order_by('-points')
              
        # Add key names, ranking and diff
        for i, v in enumerate(profiles, start=1):
            rankings.append(
                {
                    'username': v.user.username,
                    'dept': v.get_dept_display(),
                    'name': v.user.get_full_name(),
                    'rank': i,
                    'points': v.points,
                    'avatar': v.avatar.url if v.avatar else None,
                    'diff': Command.calc_diff(prev_rankings, v.user.username, i) if prev_rankings else 'NR'
                }
            )

        # Cron job runs once every day at the same time (currently at 5 AM)
        # Cache rankings for 25 hours (not 24 hours since we need it for rank calculations)
        cache.set(today_cache_key, rankings, 60 * 60 * 25)

        # Delete old ETag cache key for rankings
        cache.delete(generate_cache_key(CACHE_KEY_ETAG_RANKINGS))
        
        self.stdout.write(self.style.SUCCESS('Successfully computed rankings for {} users.'.format(len(rankings))))
