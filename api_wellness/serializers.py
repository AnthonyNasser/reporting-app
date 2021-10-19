import pytz

from datetime import timedelta
from itertools import groupby

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db.models import Sum
from django.utils import timezone
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import (Activity, ActivityLog, Event, EventLog, Category,
                     Feedback, Profile, Section, Milestone, UserMilestone,
                     Badge, UserBadge)

DAILY_MAX_LIMIT = 16
DAILY_CUSTOM_LIMIT = 3

class UserSerializer(serializers.ModelSerializer):    
    class Meta:
        model = User
        fields = ('username', 'id', 'first_name', 'last_name', 'email', 'password')
        extra_kwargs = {
            # Remove require for password and validation for username;
            # This is needed to allow updating nested serializer;
            # Will be handled manually by validation below.
            'password': {'required': False, 'write_only': True},            
            'username': {'validators': []}
        }
    
    def validate_username(self, value):
        # Validate only when creating a user
        if self.context['request'].method == 'POST':
            if User.objects.filter(username=value).exists():
                raise serializers.ValidationError('Username field must be unique.')
        return value

    def validate_email(self, value):
        # Validate only when creating a user
        if self.context['request'].method == 'POST':
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError('Email field must be unique.')
        return value
    
    def validate(self, data):
        """
        Validates password using default validators
        """
        username = data.get('username', None)
        first_name = data.get('first_name', None)
        last_name = data.get('last_name', None)
        email = data.get('email', None)
        password = data.get('password', None)

        # Username, first/last name and email are always required
        if not all([username, first_name, last_name, email]):
            raise serializers.ValidationError('username, first/last name and email are required.')

        # Password is required when creating a user
        if password is None and self.context['request'].method == 'POST':
            raise serializers.ValidationError('A password is required.')

        # Validate password if given
        if password:
            # Create temporary user for validators
            temp_user = User(
                username=data['username'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email']
            )
            # Validate password. Raises ValidationError if not valid
            validate_password(password=password, user=temp_user)      

        return data

class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ('id', 'name')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'points', 'active', 'section_id')

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ('id', 'name', 'active', 'category_id')

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'name', 'description', 'poster', 'points', 'active', 'promote', 'start', 'end', 'location', 'section_id')

class BadgeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='get_code_display')

    class Meta:
        model = Badge
        fields = ('id', 'code', 'name', 'description', 'message', 'icon', 'points', 'active')

class MilestoneSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='get_name_display')

    class Meta:
        model = Milestone
        fields = ('id', 'name', 'points')

class ActivityLogListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        logs = []
        for log in validated_data:
            logs.append(
                ActivityLog(
                    profile=log['profile_id'].profile,
                    category=log['category_id'],
                    datetime=log['datetime']
                )
            )
        return ActivityLog.objects.bulk_create(logs)
    
    def validate(self, data):
        """
        Validates multiple activity logs for unique constraints and daily limits
        """
        # Validate unique constraints
        count = len(data)
        datetimes = {log['datetime'] for log in data} # Remove duplicates
        if len(datetimes) != count:
            raise serializers.ValidationError('Activity Logs are not unique.')

        # Set current timezone
        timezone.activate(timezone=pytz.timezone('America/Los_Angeles'))
        
        # Validate limits        
        # Sort logs by datetime in current timezone
        sorted_data = sorted(data, key=lambda log: timezone.localtime(log['datetime']))
        # Group logs by date
        log_groups_by_date = []
        for k, g in groupby(sorted_data, key=lambda log: log['datetime'].date()):
            log_groups_by_date.append(list(g))

        # Get initial queryset filtered by earliest and latest logs in data
        qs = ActivityLog.objects.select_related('category').filter(
            profile=self.context['request'].user.profile,
            datetime__date__gte=sorted_data[0]['datetime'].date(), # first
            datetime__date__lte=sorted_data[-1]['datetime'].date() # last
        )
        
        for log_group in log_groups_by_date:
            # Calculate total points and total custom points for this log group
            total_points = sum([log['category_id'].points for log in log_group])
            total_custom_points = sum(
                [log['category_id'].points for log in log_group if log['category_id'].name.lower() == 'uncategorized']
            )
            # Get date for log group. Since they are grouped by date (see above),
            # the first log's date is the same as all others in the group
            date = log_group[0]['datetime'].date()

            # Check if logged points for this date already exceeds daily limit
            if total_points > DAILY_MAX_LIMIT:
                raise serializers.ValidationError(
                     'too many points logged for {}'.format(date))
            
            # Filter logs by this date
            logs = qs.filter(datetime__date=date)
            if logs:
                # Validate total daily limit
                if total_points:
                    logs_total_points = logs.values('profile').annotate(points=Sum('category__points'))
                    if total_points + logs_total_points[0]['points'] > DAILY_MAX_LIMIT:                        
                        raise serializers.ValidationError(
                            'max daily limit of {} points reached for {}.'.format(DAILY_MAX_LIMIT, date))
                
                # Validate total custom daily limit
                if total_custom_points:
                    logs_custom_total_points = logs.filter(category__name='Uncategorized') \
                                                   .values('profile').annotate(points=Sum('category__points'))
                    if logs_custom_total_points and total_custom_points + \
                            logs_custom_total_points[0]['points'] > DAILY_CUSTOM_LIMIT:
                            raise serializers.ValidationError('max daily custom limit of '
                            '{} points reached for {}.'.format(DAILY_CUSTOM_LIMIT, date))
        
        # Deactivate current timezone
        timezone.deactivate()
        
        return data

class ActivityLogSerializer(serializers.ModelSerializer):
    profile_id = serializers.ReadOnlyField(default=serializers.CurrentUserDefault())
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    
    class Meta:
        model = ActivityLog
        list_serializer_class = ActivityLogListSerializer
        fields = ('profile_id', 'category_id', 'datetime')
    
    def create(self, validated_data):
        return ActivityLog.objects.create(
            profile=validated_data['profile_id'].profile,
            category=validated_data['category_id'],
            datetime=validated_data['datetime']
        )
    
    def validate_datetime(self, value):
        """
        Validates that datetime is not in the future
        """ 
        if value > timezone.now() + timedelta(seconds=10): # Add 10 second padding for any discrepancies
            raise serializers.ValidationError('this date ({}) is in the future'.format(value))
        return value
    
    def validate(self, data):
        """
        Validates an activity log for unique constraints and daily limits
        """
        if ActivityLog.objects.filter(
            profile=data['profile_id'].profile,
            datetime=data['datetime']).exists():
            raise serializers.ValidationError('Activity Log is not unique for {}.'.format(data['datetime']))

        # Get this log's points and date
        log_points = data['category_id'].points

        # Set current timezone
        timezone.activate(timezone=pytz.timezone('America/Los_Angeles'))

        log_date = timezone.localdate(data['datetime'])
        
        # Fetch this date's activity logs for current user in current timezone
        qs = ActivityLog.objects.select_related('category') \
                .filter(profile=data['profile_id'].profile, datetime__date=log_date)
        
        if qs:
            # Validate total daily limit
            total_points = qs.values('profile').annotate(points=Sum('category__points'))
            
            if total_points[0]['points'] + log_points > DAILY_MAX_LIMIT:
                 raise serializers.ValidationError(
                     'max daily limit of {} points reached for {}.'.format(DAILY_MAX_LIMIT, log_date))
        
            if data['category_id'].name.lower() == 'uncategorized':                
                # Validate total custom daily limit
                custom_total_points = qs.filter(category__name='Uncategorized') \
                                        .values('profile').annotate(points=Sum('category__points'))
                
                if custom_total_points and custom_total_points[0]['points'] + log_points > DAILY_CUSTOM_LIMIT:
                    raise serializers.ValidationError(
                        'max daily custom limit of {} points reached for {}.'.format(DAILY_CUSTOM_LIMIT, log_date))
        
        
        # Deactivate current timezone
        timezone.deactivate()
        
        return data

class EventLogListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        logs = []
        for log in validated_data:
            logs.append(
                EventLog(
                    profile=log['profile_id'].profile,
                    event=log['event_id'],
                    datetime=log['datetime']
                )
            )
        return EventLog.objects.bulk_create(logs)
    
    def validate(self, data):
        """
        Validates multiple event logs for unique constraints and event times
        """
        # Validate unique constraints
        count = len(data)
        datetimes = {log['datetime'] for log in data} # Remove duplicates
        if len(datetimes) != count:
            raise serializers.ValidationError('Event Logs are not unique.')
        events = {log['event_id'] for log in data} # Remove duplicates
        if len(events) != count:
            raise serializers.ValidationError('The same event was logged more than once.')
        
        # for event_log in data:
        #     # Get event start and end datetimes
        #     start = event_log['event_id'].start
        #     end = event_log['event_id'].end

        #     # Current event log datetime
        #     log_datetime = event_log['datetime']

        #     # Check if log was submitted during the event. Note: All times are compared in UTC time
        #     if start > log_datetime or end < log_datetime:
        #         raise serializers.ValidationError('The event log needs to be submitted during the event: '
        #                                         'start: {} - end {}.'.format(start, end))

        return data

class EventLogSerializer(serializers.ModelSerializer):
    profile_id = serializers.ReadOnlyField(default=serializers.CurrentUserDefault())
    event_id = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all())
    
    class Meta:
        model = EventLog
        list_serializer_class = EventLogListSerializer
        fields = ('profile_id', 'event_id', 'datetime')
    
    def create(self, validated_data):
        return EventLog.objects.create(
            profile=validated_data['profile_id'].profile,
            event=validated_data['event_id'],
            datetime=validated_data['datetime']
        )
    
    def validate_datetime(self, value):
        """
        Validates that datetime is not in the future
        """
        if value > timezone.now() + timedelta(seconds=10): # Add 10 second padding for any discrepancies:
            raise serializers.ValidationError('this date ({}) is in the future'.format(value))
        return value
    
    def validate(self, data):
        """
        Validates an event log for unique constraints and event times
        """
        if EventLog.objects.filter(
            profile=data['profile_id'].profile,
            event=data['event_id']).exists():
            raise serializers.ValidationError('Event Log is not unique for {}.'.format(data['datetime']))
        
        # Get event start and end datetimes
        # start = data['event_id'].start
        # end = data['event_id'].end

        # # Current event log datetime
        # log_datetime = data['datetime']

        # # Check if log was submitted during the event. Note: All times are compared in UTC time
        # if start > log_datetime or end < log_datetime:
        #     raise serializers.ValidationError('The event log needs to be submitted during the event: '
        #                                       'start: {} - end {}.'.format(start, end))

        return data

class UserMilestoneListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        milestones = []
        for milestone in validated_data:
            milestones.append(
                UserMilestone(
                    profile=milestone['profile_id'].profile,
                    milestone=milestone['milestone_id'],
                    datetime=milestone['datetime']
                )
            )
        return UserMilestone.objects.bulk_create(milestones)
    
    def validate(self, data):
        """
        Validates multiple milestones for unique constraints
        """
        # Validate unique constraints
        count = len(data)
        datetimes = {log['datetime'] for log in data} # Remove duplicates by datetime
        if len(datetimes) != count:
            raise serializers.ValidationError('Multiple milestones found with same date and time.')
        milestones = {log['milestone_id'] for log in data} # Remove duplicates by milestone_id
        if len(milestones) != count:
            raise serializers.ValidationError('The same milestone was logged more than once.')

        return data

class UserMilestoneSerializer(serializers.ModelSerializer):
    profile_id = serializers.ReadOnlyField(default=serializers.CurrentUserDefault())
    milestone_id = serializers.PrimaryKeyRelatedField(queryset=Milestone.objects.all())
    
    class Meta:
        model = UserMilestone
        list_serializer_class = UserMilestoneListSerializer
        fields = ('profile_id', 'milestone_id', 'datetime')
    
    def create(self, validated_data):
        return UserMilestone.objects.create(
            profile=validated_data['profile_id'].profile,
            milestone=validated_data['milestone_id'],
            datetime=validated_data['datetime']
        )
    
    def validate(self, data):
        """
        Validates milestone for unique constraints
        """
        if UserMilestone.objects.filter(
            profile=data['profile_id'].profile,
            milestone=data['milestone_id']).exists():
            raise serializers.ValidationError('Milestone has already been recorded.')

        return data

class UserBadgeListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        badges = []
        for badge in validated_data:
            badges.append(
                UserBadge(
                    profile=badge['profile_id'].profile,
                    badge=badge['badge_id'],
                    datetime=badge['datetime']
                )
            )
        return UserBadge.objects.bulk_create(badges)
    
    def validate(self, data):
        """
        Validates multiple badges for duplication
        """
        milestones = {log['badge_id'] for log in data} # Remove duplicates by badge_id
        if len(milestones) != len(data):
            raise serializers.ValidationError('The same badge was logged more than once.')

        return data

class UserBadgeSerializer(serializers.ModelSerializer):
    profile_id = serializers.ReadOnlyField(default=serializers.CurrentUserDefault())
    badge_id = serializers.PrimaryKeyRelatedField(queryset=Badge.objects.all())
    
    class Meta:
        model = UserBadge
        list_serializer_class = UserBadgeListSerializer
        fields = ('profile_id', 'badge_id', 'datetime')
    
    def create(self, validated_data):
        return UserBadge.objects.create(
            profile=validated_data['profile_id'].profile,
            badge=validated_data['badge_id'],
            datetime=validated_data['datetime']
        )
    
    def validate(self, data):
        """
        Validates badges for unique constraints
        """
        if UserBadge.objects.filter(
            profile=data['profile_id'].profile,
            badge=data['badge_id']).exists():
            raise serializers.ValidationError('Badge has already been recorded.')

        return data

class ProfileSerializer(serializers.ModelSerializer):
    user        = UserSerializer()
    categories  = ActivityLogSerializer(source='activitylog_set', many=True, read_only=True)
    events      = EventLogSerializer(source='eventlog_set', many=True, read_only=True)
    badges      = UserBadgeSerializer(source='userbadge_set', many=True, read_only=True)
    milestones  = UserMilestoneSerializer(source='usermilestone_set', many=True, read_only=True)

    class Meta:
        model = Profile
        fields = ('user', 'id', 'dob', 'gender', 'dept', 'avatar', 'categories', 'events', 'badges', 'milestones')
        read_only_fields = ('avatar',)

    def create(self, validated_data):
        return Profile.objects.create_profile(validated_data)
    
    def update(self, instance, validated_data):
        return Profile.objects.update_profile(instance, validated_data)

class CategoryActivitySerializer(serializers.ModelSerializer):
    activities  = ActivitySerializer(many=True, read_only=True)
     
    class Meta: 
        model = Category
        fields = ('id', 'name', 'description', 'points', 'active', 'section_id', 'activities')

class InitializeSerializer(serializers.ModelSerializer):
    categories = CategoryActivitySerializer(many=True, read_only=True)
    events = EventSerializer(many=True, read_only=True)
    
    class Meta:
        model = Section
        fields = ('id', 'name', 'description', 'categories', 'events')

class FeedbackSerializer(serializers.ModelSerializer):
    profile_id = serializers.ReadOnlyField(default=serializers.CurrentUserDefault())
    
    class Meta:
        model = Feedback
        fields = ('message', 'datetime', 'profile_id')
    
    def create(self, validated_data):
        return Feedback.objects.create(
            profile=validated_data['profile_id'].profile,
            message=validated_data['message'],
            datetime=validated_data['datetime']
        )
