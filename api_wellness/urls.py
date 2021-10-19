from django.conf.urls import include, url
from rest_framework import generics, routers
from rest_framework.permissions import AllowAny

from . import views
from .models import Section
from .serializers import InitializeSerializer

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'activities', views.ActivityViewSet)
router.register(r'sections', views.SectionViewSet)
router.register(r'events', views.EventViewSet)
router.register(r'badges', views.BadgeViewSet)
router.register(r'milestones', views.MilestoneViewSet)
router.register(r'activity-logs', views.ActivityLogViewSet)
router.register(r'event-logs', views.EventLogViewSet)
router.register(r'user-milestones', views.UserMilestoneViewSet)
router.register(r'user-badges', views.UserBadgeViewSet)
router.register(r'feedback', views.FeedbackViewSet)

urlpatterns = [
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # Register and token routes
    url(r'^register/', views.register, name='register'),
    url(r'^get-token/', views.get_token, name='get-token'),
    # Password reset routes    
    url(r'^request-password-reset/', views.request_password_reset, name='request-password-reset'),
    url(r'^verify-code/', views.verify_code, name='verify-code'),
    url(r'^change-password/', views.change_password, name='change-password'),
    # Initialize clients
    url(r'^initialize/', generics.ListAPIView.as_view(
                         queryset=Section.objects.prefetch_related('categories__activities', 'events'),
                         serializer_class=InitializeSerializer,
                         permission_classes=[AllowAny]), name='initialize'),
    # Misc
    url(r'^check-availability/', views.check_availability, name='check-availability'),
]

urlpatterns += router.urls
