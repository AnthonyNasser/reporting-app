from django.contrib import admin
from django import forms

# Add models to make them editable in admin site
from .models import Category, Item, User, Reservation, Department
from .widgets import FilteredSelectMultiple

class UserAdmin(admin.ModelAdmin):
	# Set the order of fields in admin page
	# Format of field sets (sections): (name, field_options)
	fieldsets = [
		(None, {'fields': ['first_name', 'last_name', 'sid', 'email', 'phone', 'title', 'department']}),		
	]
	# Column names to display in list page
	list_display  = ('first_name', 'last_name', 'email', 'phone', 'sid', 'title', 'department')	
	# Add search capability
	search_fields = ['^first_name', '^last_name', 'sid', 'department']
	# Add filter capabily 
	list_filter   = ['title', 'department']

class ItemAdmin(admin.ModelAdmin):
	# Set the order of fields in admin page
	# Format of field sets (sections): (name, field_options)
	fieldsets = [
		('Description',		 		{'fields': ['name', 'label', 'model', 'serial']}),
		('Condition', 				{'fields': ['condition']}),		
		('Category',				{'fields': ['category']}),
		('Notes', 					{'fields': ['misc']}),
	]
	# Column names to display in list page
	list_display  = ('name', 'label', 'category', 'condition')
	# Add search capability
	search_fields = ['name', 'category__name', 'label']
	# Add filter capability 
	list_filter   = ['category']

class DepartmentAdmin(admin.ModelAdmin):
	# Set the order of fields in admin page
	# Format of field sets (sections): (name, field_options)
	fieldsets = [
		('Department',		 			{'fields': ['name', 'color']}),
	]
	# Column names to display in list page
	list_display  = ('name', 'color')
	# Add search capability
	search_fields = ['name']

class ReservationAdminForm(forms.ModelForm):	
	# Use FilteredSelectMultiple for following fields
	items = forms.ModelMultipleChoiceField(
		queryset	=	Item.objects.all(),
		widget 		=	FilteredSelectMultiple(verbose_name='items', is_stacked=False)
	)
	#crew = forms.ModelMultipleChoiceField(
		# Limit queryset to crew only
	#	queryset	=	User.objects.filter(title__exact='C'),
	#	widget 		=	FilteredSelectMultiple(verbose_name='crew', is_stacked=False)
	#)

class ReservationAdmin(admin.ModelAdmin):
	# Set the order of fields in admin page
	# Format of field sets (sections): (name, field_options)	
	fieldsets = [
		('Project', 			{'fields': ['project']}),
		('Reserved To', 		{'fields': ['user']}),		
		('Date Range',			{'fields': ['start_date', 'end_date']}),
		('Item List',			{'fields': ['items']}),
		('Crew', 				{'fields': ['crew']}),
		('Additional Notes', 	{'fields': ['comment']}),
		('State', 				{'fields': ['state']})
	]
	# Form to use
	form = ReservationAdminForm
	# Column names to display in list page
	list_display  = ('user', 'project', 'start_date', 'end_date', 'state')
	# Add filter capability
	list_filter   = ['user', 'start_date', 'state']
	# Add search capability
	search_fields = ['project', '^user__first_name', '^user__last_name']


admin.site.register(Category)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Reservation, ReservationAdmin)