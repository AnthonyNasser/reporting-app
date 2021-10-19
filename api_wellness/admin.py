import pytz

from django.contrib import admin
from django.utils import timezone

from .models import (Activity, ActivityLog, Category, Event, EventLog,
                     Feedback, Profile, Section, Milestone, Badge,
					 UserBadge, UserMilestone)


def get_local_datetime(instance):
	return timezone.localtime(value=instance.datetime, timezone=pytz.timezone('America/Los_Angeles'))
get_local_datetime.short_description = 'Date & Time'

class EventAdmin(admin.ModelAdmin):
	# Set the order of fields in admin page
	# Format of field sets (sections): (name, field_options)
	fieldsets = [
		('Section', {'fields': ['section']}),
		('Event Information', {
			'fields': ['name', 'description', 'poster', 'start', 'end', 'location']
		}),
		(None, {'fields': ['points', 'active', 'promote']}),
	]
	# Column names to display in list page
	list_display  = ('name', 'start', 'end', 'points', 'active', 'promote')	
	# Add search capability
	search_fields = ['name']
	# Add filter capability 
	list_filter   = ['start', 'active', 'promote']

class SectionAdmin(admin.ModelAdmin):
	# Set the order of fields in admin page	
	# Format of field sets (sections): (name, field_options)
	fieldsets = [
		('Section Description', {'fields': ['name', 'description', 'active']}),
	]
	# Column names to display in list page
	list_display  = ('name', 'active')	
	# Add search capability
	search_fields = ['name']
	# Add filter capability 
	list_filter   = ['active']

class CategoryAdmin(admin.ModelAdmin):
	# Set the order of fields in admin page	
	# Format of field sets (sections): (name, field_options)
	fieldsets = [
		('Category Description', {'fields': ['name', 'description', 'points', 'active', 'section']}),
	]
	# Column names to display in list page
	list_display  = ('name', 'points', 'section', 'active')	
	# Add search capability
	search_fields = ['name']
	# Add filter capability 
	list_filter   = ['section', 'active']

class ActivityAdmin(admin.ModelAdmin):
	# Set the order of fields in admin page	
	# Format of field sets (sections): (name, field_options)
	fieldsets = [
		('Activity Description', {'fields': ['name', 'active', 'category']}),
	]
	# Column names to display in list page
	list_display  = ('name', 'category', 'get_section_name', 'active')	
	# Add search capability
	search_fields = ['name']
	# Add filter capability 
	list_filter   = ['category', 'category__section', 'active']

	def get_section_name(self, instance):
		return instance.category.section	
	get_section_name.short_description = 'Section'

class MilestoneAdmin(admin.ModelAdmin):
	# Set the order of fields in admin page	
	# Format of field sets (sections): (name, field_options)
	fieldsets = [
		('Milestone Information', {'fields': ['name', 'points']}),
	]
	# Column names to display in list page
	list_display  = ('name', 'points')	
	# Add search capability
	search_fields = ['name']

class BadgeAdmin(admin.ModelAdmin):
	# Set the order of fields in admin page	
	# Format of field sets (sections): (name, field_options)
	fieldsets = [
		('Badge Information', {'fields': ['code', 'description', 'message', 'points', 'active']}),
		('Badge Icon', {'fields': ['icon']}),
	]
	# Column names to display in list page
	list_display  = ('code', 'points', 'active')	
	# Add search capability
	search_fields = ['code']

class ProfileAdmin(admin.ModelAdmin):
	# Set the order of fields in admin page	
	# Format of field sets (sections): (name, field_options)
	fieldsets = [
		('Profile Information', {'fields': ['user', 'dob', 'gender', 'avatar']}),
		('Campus Information', {'fields': ['id', 'dept']}),
	]
	# Column names to display in list page
	list_display  = ('get_full_name', 'get_email', 'id', 'gender', 'dept')
	# Add search capability
	search_fields = ['^user__first_name', '^user__last_name', 'id']
	# Add filter capability 
	list_filter   = ['gender', 'dept']

	def get_full_name(self, instance):
		return instance.user.get_full_name()	
	get_full_name.short_description = 'Name'

	def get_email(self, instance):
		return instance.user.email	
	get_email.short_description = 'Email'

class ActivityLogAdmin(admin.ModelAdmin):
	# Column names to display in list page
	list_display  = ('profile', 'category', 'get_category_points', get_local_datetime)

	def get_category_points(self, instance):
		return instance.category.points
	get_category_points.short_description = 'Points'

class EventLogAdmin(admin.ModelAdmin):
	# Column names to display in list page
	list_display  = ('profile', 'event', 'get_event_points', get_local_datetime)

	def get_event_points(self, instance):
		return instance.event.points
	get_event_points.short_description = 'Points'

class UserMilestoneAdmin(admin.ModelAdmin):
	# Column names to display in list page
	list_display  = ('profile', 'milestone', 'get_milestone_points', get_local_datetime)

	def get_milestone_points(self, instance):
		return instance.milestone.points
	get_milestone_points.short_description = 'Points'

class UserBadgeAdmin(admin.ModelAdmin):
	# Column names to display in list page
	list_display  = ('profile', 'badge', 'get_badge_points', get_local_datetime)

	def get_badge_points(self, instance):
		return instance.badge.points
	get_badge_points.short_description = 'Points'

class FeedbackAdmin(admin.ModelAdmin):
	# Column names to display in list page
	list_display  = ('profile', 'message', get_local_datetime)

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Milestone, MilestoneAdmin)
admin.site.register(Badge, BadgeAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(ActivityLog, ActivityLogAdmin)
admin.site.register(EventLog, EventLogAdmin)
admin.site.register(UserMilestone, UserMilestoneAdmin)
admin.site.register(UserBadge, UserBadgeAdmin)
admin.site.register(Feedback, FeedbackAdmin)
