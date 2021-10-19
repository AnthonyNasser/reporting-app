import pytz

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import Group, Permission, User
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db.models import Q
from django.utils import timezone
from guardian.shortcuts import assign_perm
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import (api_view, detail_route, list_route,
                                       parser_classes, permission_classes,
                                       throttle_classes)
from rest_framework.exceptions import NotAuthenticated, NotFound, ParseError
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import (AllowAny, DjangoModelPermissions,
                                        DjangoObjectPermissions)
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from rest_framework_jwt.settings import api_settings

from .constants import (CACHE_KEY_ETAG_LATEST_EVENTS, CACHE_KEY_ETAG_RANKINGS,
                        CACHE_KEY_LATEST_EVENTS_TIMESTAMP, CACHE_KEY_RANKINGS)
from .models import (Activity, ActivityLog, Category, Event, EventLog,
                     Feedback, Profile, Section, Milestone, UserMilestone,
                     Badge, UserBadge)
from .serializers import (ActivityLogSerializer, ActivitySerializer,
                          CategorySerializer, EventLogSerializer,
                          EventSerializer, FeedbackSerializer,
                          ProfileSerializer, SectionSerializer,
                          MilestoneSerializer, BadgeSerializer,
                          UserBadgeSerializer, UserMilestoneSerializer)
from .utils import (RegisterThrottle, confirm_etag, generate_cache_key,
                    generate_etag, set_cache_headers)


class UserViewSet(mixins.ListModelMixin, # list()
                 mixins.RetrieveModelMixin, # retrieve()
                 mixins.UpdateModelMixin, # update()
                 viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed, created and edited.
    """
    queryset = User.objects.none() # Sentinel queryset required for DjangoModelPermissions
    serializer_class = ProfileSerializer

    def get_queryset(self):
        """
        This view should return the profile for the currently authenticated user.
        """
        user = self.request.user
        if user.is_staff: # For staff access to API root view
            return Profile.objects.select_related('user').prefetch_related('activitylog_set', 'eventlog_set').order_by('user')
        elif not hasattr(user, 'profile'): # Check if user has a profile
            return self.queryset
        else:
            return Profile.objects.select_related('user').prefetch_related('activitylog_set', 'eventlog_set').filter(user=user)
    
    @detail_route(methods=['put'], url_path='set-password', permission_classes=[DjangoObjectPermissions])
    def set_password(self, request, pk=None):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not (old_password and new_password):
            raise ParseError('Required parameters missing.')

        if user.check_password(old_password):
            try:
                validate_password(password=new_password, user=user)
            except ValidationError as e:
                raise serializers.ValidationError(e)

            user.set_password(new_password)
            user.save()
            # Generate new token
            token, exp = generate_jwt_token(user)
            return Response({'token': token, 'exp': exp})
        else:
            raise NotAuthenticated('Incorrect password.')
    
    @detail_route(methods=['put'], url_path='set-username', permission_classes=[DjangoObjectPermissions])
    def set_username(self, request, pk=None):
        user = request.user
        new_username = request.data.get('username')

        if not new_username:
            raise ParseError('Required parameter missing.')

        user.username = new_username
        user.save()
        # Generate new token
        token, exp = generate_jwt_token(user)
        return Response({'token': token, 'exp': exp})
    
    @detail_route(url_path='get-rank', permission_classes=[DjangoObjectPermissions])
    def get_rank(self, request, pk=None):
        """
        Returns the user's rank for today
        """
        # Check for ETags
        if confirm_etag(request, CACHE_KEY_ETAG_RANKINGS):
            return Response(status=status.HTTP_304_NOT_MODIFIED)
        
        # Return cache response if available
        user = request.user
        cache_key = generate_cache_key(CACHE_KEY_RANKINGS.format(timezone.localdate(timezone=pytz.timezone('America/Los_Angeles'))))
        rankings = cache.get(cache_key)
        response = None
        rank = None
        points = 0
        if rankings is not None:
            for ranking in rankings:
                if user.username == ranking['username']:
                    rank = ranking['rank']
                    points = ranking['points']
                    break
            else:
                rank = 'NR' # Not ranked

            response = Response({'rank': rank, 'points': points})
            # Create ETag
            etag = generate_etag(CACHE_KEY_ETAG_RANKINGS, rankings)
            if etag:
                return set_cache_headers(response, etag)
            return response
        else:
            raise NotFound('User\'s rank is not available at this time. Please check back tomorrow.')
    
    @detail_route(url_path='renew-token', permission_classes=[DjangoObjectPermissions])
    def renew_token(self, request, pk=None):
        """
        Renews and returns user's token
        """
        token, exp = generate_jwt_token(request.user)
        return Response({'token': token, 'exp': exp})
    
    @list_route()
    def rankings(self, request):
        """
        Returns the rankings for the day
        """
        # Check for ETags
        if confirm_etag(request, CACHE_KEY_ETAG_RANKINGS):
            return Response(status=status.HTTP_304_NOT_MODIFIED)
        
        # Return cache response if available
        cache_key = generate_cache_key(CACHE_KEY_RANKINGS.format(timezone.localdate(timezone=pytz.timezone('America/Los_Angeles'))))
        rankings = cache.get(cache_key)
        response = None
        if rankings is not None:
            response = Response(rankings)
            # Create ETag
            etag = generate_etag(CACHE_KEY_ETAG_RANKINGS, rankings)
            if etag:
                return set_cache_headers(response, etag)
            return response
        else:
            raise NotFound('No rankings available at this time. Please check back tomorrow.')

    @detail_route(methods=['put'], permission_classes=[DjangoObjectPermissions],
                parser_classes=[FileUploadParser], url_path='set-avatar')
    def set_avatar(self, request, pk=None):
        """
        This view allows a user to add an avatar to their profile
        Requires following HTTP header:
        << Content-Disposition: attachment; filename=avatar.jpg >>
        """
        avatar = request.data['file']
        user = request.user
        if avatar is not None:
            profile = user.profile
            # Delete current avatar image
            if profile.avatar:
                profile.avatar.delete()
            # Save new avatar image
            profile.avatar.save(avatar.name, avatar)
            return Response({'location': profile.avatar.url}, status=status.HTTP_201_CREATED, headers={'Location': profile.avatar.url})
        
        return Response(status=status.HTTP_204_NO_CONTENT)

class CategoryViewSet(viewsets.ReadOnlyModelViewSet): # list() and retrieve() only
    """
    API endpoint that allows categories to be listed or retrieved by id.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ActivityViewSet(viewsets.ReadOnlyModelViewSet): # list() and retrieve() only
    """
    API endpoint that allows activities to be listed or retrieved by id.
    """
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer

class EventViewSet(viewsets.ReadOnlyModelViewSet): # list() and retrieve() only
    """
    API endpoint that allows events to be listed or retrieved by id.
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    @list_route()
    def latest(self, request):
        """
        Returns the latest new or modified events
        """
        # Check for ETags
        if confirm_etag(request, CACHE_KEY_ETAG_LATEST_EVENTS):
            return Response(status=status.HTTP_304_NOT_MODIFIED)
        
        # Check for latest events timestamp
        cache_key = generate_cache_key(CACHE_KEY_LATEST_EVENTS_TIMESTAMP)
        cache_timestamp = cache.get(cache_key)

        if cache_timestamp is not None:
            # Check if latest events need to be updated
            latest_events = Event.objects.filter(last_modified__gte=cache_timestamp)
            if latest_events.exists():
                timestamp = timezone.now()
                # Update cached timestamp
                cache.set(cache_key, timestamp, None)
                # Generate ETag for new timestamp
                etag = generate_etag(CACHE_KEY_ETAG_LATEST_EVENTS, timestamp)
            else: # User does not have an ETag
                # Return latest events (not including passed events)
                latest_events = Event.objects.filter(end__gte=cache_timestamp)
                # Generate ETag
                etag = generate_etag(CACHE_KEY_ETAG_LATEST_EVENTS, cache_timestamp)
        else:
            timestamp = timezone.now()
            # Return current snapshot of latest events (not including passed events)
            latest_events = Event.objects.filter(end__gte=timestamp)
            # Cache timestamp
            cache.set(cache_key, timestamp, None)
            # Generate ETag
            etag = generate_etag(CACHE_KEY_ETAG_LATEST_EVENTS, timestamp)

        serializer = self.get_serializer(latest_events, many=True, context={'request': request})
        response = Response(serializer.data)
        
        if etag:
            return set_cache_headers(response, etag)
        return response            

class SectionViewSet(viewsets.ReadOnlyModelViewSet): # list() and retrieve() only
    """
    API endpoint that allows sections to be listed or retrieved by id.
    """
    queryset = Section.objects.all()
    serializer_class = SectionSerializer

    @list_route()
    def custom(self, request):
        return Response({
            'video_id': 'tZCa82xdImo',
            'video_bg': request.build_absolute_uri(settings.MEDIA_URL + 'custom-video-bg.jpg')
        })

class ActivityLogViewSet(mixins.CreateModelMixin, # create()
                 mixins.ListModelMixin, # list()
                 mixins.RetrieveModelMixin, # retrieve()
                 viewsets.GenericViewSet):
    """
    API endpoint that allows activity logs to be viewed and created.
    """
    queryset = ActivityLog.objects.none() # Sentinel queryset required for DjangoModelPermissions
    serializer_class = ActivityLogSerializer

    def get_queryset(self):
        """
        This view should return a list of all the activity
        logs for the current authenticated user.
        """
        user = self.request.user
        if user.is_staff: # For staff access to API root view
            return ActivityLog.objects.order_by('-datetime')
        elif not hasattr(user, 'profile'): # Check if user has a profile
            return self.queryset
        else:
            return ActivityLog.objects.select_related('profile').filter(profile__user=user).order_by('-datetime')
    
    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):
            serializer = self.get_serializer(data=request.data, many=True, allow_empty=False)
        else:
            serializer = self.get_serializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class EventLogViewSet(mixins.CreateModelMixin, # create()
                 mixins.ListModelMixin, # list()
                 mixins.RetrieveModelMixin, # retrieve()
                 viewsets.GenericViewSet):
    """
    API endpoint that allows event logs to be viewed and created.
    """
    queryset = EventLog.objects.none() # Sentinel queryset required for DjangoModelPermissions
    serializer_class = EventLogSerializer

    def get_queryset(self):
        """
        This view should return a list of all the event
        logs for the current authenticated user.
        """
        user = self.request.user
        if user.is_staff: # For staff access to API root view
            return EventLog.objects.order_by('-datetime')
        elif not hasattr(user, 'profile'): # Check if user has a profile
            return self.queryset
        else:
            return EventLog.objects.select_related('profile').filter(profile__user=user).order_by('-datetime')
    
    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):
            serializer = self.get_serializer(data=request.data, many=True, allow_empty=False)
        else:
            serializer = self.get_serializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class UserMilestoneViewSet(mixins.CreateModelMixin, # create()
                 mixins.ListModelMixin, # list()
                 mixins.RetrieveModelMixin, # retrieve()
                 viewsets.GenericViewSet):
    """
    API endpoint that allows milestones to be viewed and created.
    """
    queryset = UserMilestone.objects.none() # Sentinel queryset required for DjangoModelPermissions
    serializer_class = UserMilestoneSerializer

    def get_queryset(self):
        """
        This view should return a list of all the achieved
        milestones for the current authenticated user.
        """
        user = self.request.user
        if user.is_staff: # For staff access to API root view
            return UserMilestone.objects.order_by('-datetime')
        elif not hasattr(user, 'profile'): # Check if user has a profile
            return self.queryset
        else:
            return UserMilestone.objects.select_related('profile').filter(profile__user=user).order_by('-datetime')
    
    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):
            serializer = self.get_serializer(data=request.data, many=True, allow_empty=False)
        else:
            serializer = self.get_serializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def perform_create(self, serializer):
        user_milestone = serializer.save()
        self.send_email(user_milestone)
    
    def send_email(self, user_milestone):
        # Get email for milestone
        email_content = user_milestone.milestone.get_email_content(milestone=user_milestone.milestone.name)

        # Send email to user
        user_milestone.profile.user.email_user(
            email_content['subject'].format(email_content['milestone'].capitalize()),
            email_content['message'].format(email_content['milestone']), # TODO: Make a plain message
            from_email='asiactive@asicsulb.org',
            html_message=email_content['message'].format(email_content['milestone'])
        )

class UserBadgeViewSet(mixins.CreateModelMixin, # create()
                 mixins.ListModelMixin, # list()
                 mixins.RetrieveModelMixin, # retrieve()
                 viewsets.GenericViewSet):
    """
    API endpoint that allows badges to be viewed and created.
    """
    queryset = UserBadge.objects.none() # Sentinel queryset required for DjangoModelPermissions
    serializer_class = UserBadgeSerializer

    def get_queryset(self):
        """
        This view should return a list of all the obtained
        badges for the current authenticated user.
        """
        user = self.request.user
        if user.is_staff: # For staff access to API root view
            return UserBadge.objects.order_by('-datetime')
        elif not hasattr(user, 'profile'): # Check if user has a profile
            return self.queryset
        else:
            return UserBadge.objects.select_related('profile').filter(profile__user=user).order_by('-datetime')
    
    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):
            serializer = self.get_serializer(data=request.data, many=True, allow_empty=False)
        else:
            serializer = self.get_serializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class FeedbackViewSet(mixins.CreateModelMixin, # create()
                 mixins.ListModelMixin, # list()
                 mixins.RetrieveModelMixin, # retrieve()
                 viewsets.GenericViewSet):
    """
    This view allows a user to send feedback
    """
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

class BadgeViewSet(viewsets.ReadOnlyModelViewSet): # list() and retrieve() only
    """
    API endpoint that allows badges to be listed or retrieved by id.
    """
    queryset = Badge.objects.none() # Sentinel queryset required for DjangoModelPermissions
    serializer_class = BadgeSerializer

    def get_queryset(self):
        """
        This view should return all badges for staff users
        and only active badges for authenticated users.
        """
        user = self.request.user
        if user.is_staff: # For staff access to API root view
            return Badge.objects.all()
        elif not hasattr(user, 'profile'): # Check if user has a profile
            return self.queryset
        else:
            return Badge.objects.filter(active=True)

class MilestoneViewSet(viewsets.ReadOnlyModelViewSet): # list() and retrieve() only
    """
    API endpoint that allows badges to be listed or retrieved by id.
    """
    queryset = Milestone.objects.all()
    serializer_class = MilestoneSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([RegisterThrottle])
def register(request):
    """
    Registers a new user with the API
    """
    serializer = ProfileSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    profile = serializer.save()
    
    # Give user all needed permissions
    assign_permissions(profile)

    # Include token
    data = serializer.data
    data['token'], data['exp'] = generate_jwt_token(profile.user)

    return Response(data, status=status.HTTP_201_CREATED, headers={'Location': reverse('api:user-detail', args=[data['user']['id']], request=request)})

def assign_permissions(profile):
    """
    Assigns default permissions to user
    """
    # Get User
    user = profile.user

    # Give user permission to their profile instance (object level permission)
    assign_perm('change_profile', user, obj=profile) # PUT/PATCH to Profile instance

    # Get or create group if needed    
    group, created = Group.objects.get_or_create(name='wellness_app')
    if created: # If group newly created, add default model level permissions
        permissions = (
            Permission.objects.get(codename='change_profile'), # PUT/PATCH to Profile
            Permission.objects.get(codename='add_activitylog'), # POST to ActivityLog
            Permission.objects.get(codename='add_eventlog'), # POST to EventLog
            Permission.objects.get(codename='add_usermilestone'), # POST to UserMilestone
            Permission.objects.get(codename='add_userbadge'), # POST to UserBadge
            Permission.objects.get(codename='add_feedback'), # POST to Feedback
        )            
        # Add permissions to group
        group.permissions.add(*permissions)
    
    # Add user to group
    user.groups.add(group)

def generate_jwt_token(user):
    """
    Function to generate a JWT for given user
    """
    # Function to generate JWT token
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

    # Generate JWT payload
    payload = jwt_payload_handler(user)

    # Return encoded JWT payload and expiration date and time
    return (jwt_encode_handler(payload), timezone.now() + api_settings.JWT_EXPIRATION_DELTA)

@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request):
    """
    This view generates a token given a valid username and password 
    """
    serializer = JSONWebTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response({
        'token': serializer.object.get('token'),
        'exp': timezone.now() + api_settings.JWT_EXPIRATION_DELTA
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    """
    This view sends a code to user's email to initiate a password reset 
    """
    email = request.data.get('email', None)

    if not email:
        # If required data not given, prevent information leakage
        return Response(status=status.HTTP_204_NO_CONTENT)

    # Check if email exists
    if User.objects.filter(email=email).exists():
        message = ('You\'re receiving this email because you requested '
                  'a password reset for your ASI Active mobile account.\n\n'
                  'Please enter the following code in the app to continue: {}')
        # Generate a random code
        code = User.objects.make_random_password(
            length=6,
            allowed_chars='ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
        )
         # Send email
        send_mail(
            'Password Reset Request',
            message.format(code),
            'asiactive@asicsulb.org',
            [email],
            fail_silently=True
        )

        # TODO: Catch errors when sending email

        # Cache the hashed code for 15 minutes
        cache.set(email, make_password(code), 60 * 15)

    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_code(request):
    """
    This view verifies the code for a password reset request
    """
    email = request.data.get('email', None)
    code = request.data.get('code', None)

    if not (email and code):
        # If required data not given, prevent information leakage
        return Response(status=status.HTTP_204_NO_CONTENT)

    # Get code from cache
    cached_code = cache.get(email)
    if cached_code is not None:
        if check_password(code, cached_code): # True if codes match
            return Response({'status': 'code confirmed'})
        else:
            raise serializers.ValidationError('Code mismatch. Please confirm and re-enter the code.')
    else:
        raise NotFound('Code not found or expired. Please request a new code.')

@api_view(['POST'])
@permission_classes([AllowAny])
def change_password(request):
    """
    This view allows a user to change their password
    """
    email = request.data.get('email', None)
    code = request.data.get('code', None)
    new_password = request.data.get('password', None)

    if not (email and code and new_password):
        # If required data not given, prevent information leakage
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    # Get code from cache
    cached_code = cache.get(email)
    if cached_code is not None:
        if check_password(code, cached_code): # True if codes match
            user = User.objects.get(email=email)
            
            try:
                # Validate password. Raises ValidationError if not valid
                validate_password(password=new_password, user=user)
            except ValidationError as e:
                raise serializers.ValidationError(e)

            # Set new password
            user.set_password(new_password)
            user.save()
            # Delete key from cache
            cache.delete(email)
            return Response({'status': 'password set successfully'})
    else:
        raise NotFound('Code not found or expired. Please request a new code.')

@api_view(['POST'])
@permission_classes([AllowAny])
def check_availability(request):
    """
    This view checks availability of username, email or staff id for registration
    """
    username = request.data.get('username', None)
    email = request.data.get('email', None)
    id = request.data.get('id', None)
    
    if not (username or email or id):
        # If required data not given, prevent information leakage
        return Response(status=status.HTTP_204_NO_CONTENT)
        
    if Profile.objects.filter(Q(user__username__iexact=username) |
                              Q(user__email__iexact=email) |
                              Q(id=id)).exists():
        raise serializers.ValidationError('Username, email and/or staff id is not unique.')
    
    return Response({'status': 'Username, email and/or staff id is available.'})
