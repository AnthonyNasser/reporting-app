from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Value as V
from django.db.models.functions import Concat
from datetime import timedelta
from .models import Reservation, User, Category, Item, ReservationForm, Log
from .signals import reserve_event


@login_required
def index(request):
	return render(request, 'reservations/base_instructions.html')

@login_required
def calendar(request):
	return render(request, 'reservations/base_calendar.html')

@login_required
def most_popular(request):
	reservations = Reservation.objects.prefetch_related('items__category').values('items__id', 'items__name', 'items__category_id').annotate(count=Count('items')).order_by('-count')[:20]
	return HttpResponse(reservations)

@login_required
def reserve(request, id=None, date=None):		
	reservation = None
	form = None
	if request.method == 'POST':
		if request.POST.get('reserve'):			
			form, reservation = save_reservation(request, id)
			if form.is_valid():
				# Signal Reservation Created
				reserve_event.send(sender=Reservation, event=Log.LOG_EVENT_CREATED, instance=reservation)

				# Notify user
				messages.success(request, 'Reservation request has been submitted successfully. Please check your email for approval.')

				# Redirect to calendar view
				return HttpResponseRedirect(reverse('reservations:calendar'))
		elif request.POST.get('checkout') and id is not None and request.user.is_staff:
			# Checkout reservation
			Reservation.objects.filter(pk=id).update(state=Reservation.STATE_CHECKOUT)
			
			# Signal Reservation Checked Out
			reserve_event.send(sender=Reservation, event=Log.LOG_EVENT_CHECKED_OUT, instance=Reservation.objects.get(pk=id))

			# Notify user
			messages.success(request, 'Reservation has been checked out successfully. Please proceed to pick up your equipment.')

			# Redirect to calendar view
			return HttpResponseRedirect(reverse('reservations:calendar'))
		elif request.POST.get('save') and id is not None:
			# Save reservation
			form, reservation = save_reservation(request, id)

			if form.is_valid():
				# Signal Reservation Saved
				reserve_event.send(sender=Reservation, event=Log.LOG_EVENT_SAVED, instance=reservation)

				# Notify user
				messages.success(request, 'Reservation has been saved successfully.')

				# Return to reservation page
				return HttpResponseRedirect(reverse('reservations:reserve-edit', args=(id,)))
		elif request.POST.get('checkin') and id is not None and request.user.is_staff:
			# Checkin reservation
			Reservation.objects.filter(pk=id).update(state=Reservation.STATE_CHECKIN)

			# Signal Reservation Checked In
			reserve_event.send(sender=Reservation, event=Log.LOG_EVENT_CHECKED_IN, instance=Reservation.objects.get(pk=id))

			# Get items for given reservation
			items = Reservation.objects.prefetch_related('items').get(pk=id).items.all()

			# Update item(s) comments if provided
			for item in items:
				if request.POST[str(item.id)]:
					Item.objects.filter(pk=item.id).update(misc=Concat('misc', V(request.POST[str(item.id)]), V('\n')))

			# Notify user
			messages.success(request, 'Reservation has been checked in successfully.')

			# Redirect to calendar view
			return HttpResponseRedirect(reverse('reservations:calendar'))
		elif request.POST.get('delete') and id is not None:			
			if send_email(request, id):				
				reservation = delete_reservation(id)

				# Signal Reservation Checked In
				reserve_event.send(sender=Reservation, event=Log.LOG_EVENT_DELETED, instance=reservation)

				# Notify user
				messages.success(request, 'Reservation has been deleted successfully and producer notified.')
			else:
				messages.warning(request, 'Reservation was not found.')

			# Redirect to calendar view
			return HttpResponseRedirect(reverse('reservations:calendar'))
	elif id is not None: # If displaying an existing reservation
		try:
			reservation = Reservation.objects.select_related('user__department').prefetch_related('items').get(pk=id)
		except ObjectDoesNotExist:
			messages.warning(request, 'Reservation was not found. It may have been deleted or declined. Please check the Activity Log for more information.')
	
	# Fetch all producers
	user_list = User.objects.select_related('department').values('id', 'first_name', 'last_name', 'sid', 'department__name')
	
	# Fetch all items
	item_list = Item.objects.values('id', 'name', 'label')

	# Fetch all reserved items
	reserved_item_list = Reservation.objects.select_related('user').prefetch_related('items').filter(start_date__gte=timezone.now()).values('start_date', 'end_date', 'user__first_name', 'user__last_name', 'items__id')
	
	context = {
		'user_list': user_list,
		'item_list': json.dumps(list(item_list), cls=DjangoJSONEncoder),
		'reserved_item_list': json.dumps(list(reserved_item_list), cls=DjangoJSONEncoder),
		'reservation': reservation,
		'date': date,
		'form': form
	}

	return render(request, 'reservations/base_reservation.html', context)

@login_required
def inventory(request, id=None):	
	if request.method == 'POST' and id is not None:
		# Fetch new comment
		if request.POST.get('comment'):
			comment = request.POST['comment']			
			try:
				# Get item
				item = Item.objects.get(pk=id)
				
				# Update and save
				item.misc += comment + '\n'
				item.save()

				# Construct email message
				message = (Reservation.EMAIL_ADMIN_INVENTORY_COMMENT % (item.name, item.label, comment))

				# Send email to admins
				send_mail('New Equipment Comment', message, 'noreply@asicsulb.org', User.ERS_ADMINS)

				# Notify user
				messages.success(request, 'Comment has been added successfully to {} - {}.'.format(item.name, item.label))
			except ObjectDoesNotExist:
				messages.warning(request, 'Could not add comment. Item may have been deleted.')
		
		# Redirect to inventory page
		return HttpResponseRedirect(reverse('reservations:inventory'))
	
	categories =  Category.objects.prefetch_related('items')
	return render(request, 'reservations/base_inventory.html', {'categories': categories})

@login_required
def get_reservations_for_month(request):
	start = request.GET['start']
	end = request.GET['end']

	# Return only approved reservations within the given date range	
	return JsonResponse(list(Reservation.objects.filter(start_date__gte=start, end_date__lte=end, state__gte=Reservation.STATE_APPROVED).select_related('user__department')
			.values('id', 'start_date', 'end_date', 'project', 'user__first_name', 'user__last_name', 'user__department__color')), safe=False)

@login_required
def approve(request, id=None):
	if request.method == 'GET' and request.user.is_staff: # Show form to approve or decline a reservation
		if id is not None:			
			try:
				# Get reservation details
				reservation = Reservation.objects.select_related('user').prefetch_related('items').get(pk=id)

				# Show reservation approval/checkin page
				return render(request, 'reservations/base_reservation_approve.html', {'reservation': reservation})
			except ObjectDoesNotExist:
				return HttpResponse("Reservation not found!")
	elif request.method == 'POST' and request.user.is_staff:
		# Check whether approved or declined
		if request.POST.get('approve'):
			if id is not None:
				# Approve reservation
				Reservation.objects.filter(pk=id).update(state=Reservation.STATE_APPROVED)

				# Signal Reservation Approved
				reserve_event.send(sender=Reservation, event=Log.LOG_EVENT_APPROVED, instance=Reservation.objects.get(pk=id))

				if send_email(request, id):
					# Notify user
					messages.success(request, 'Reservation has been approved.')
				else:
					HttpResponse("There were problems approving this reservation.")

		elif request.POST.get('decline'):
			if id is not None:
				if send_email(request, id):
					reservation = delete_reservation(id)

					# Signal Reservation Declined
					reserve_event.send(sender=Reservation, event=Log.LOG_EVENT_DECLINED, instance=reservation)

					# Notify user
					messages.success(request, 'Reservation has been declined.')
				else:
					messages.warning(request, 'Reservation was not found.')
			else:
				HttpResponse("There were problems declining this reservation.")

		# Redirect to calendar view
		return HttpResponseRedirect(reverse('reservations:calendar'))
	else:
		return HttpResponse("Your account does not have access to this resource. Please contact your supervisor if you feel this is an error.")

@login_required
def activity_log(request):
	logs_list = Log.objects.select_related('reservation__user')
	paginator = Paginator(logs_list, 50)

	page = request.GET.get('page', 1)
	try:
		logs = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, return first page
		logs = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), return last page
		logs = paginator.page(paginator.num_pages)

	return render(request, 'reservations/base_activity_log.html', {'logs': logs})

#
########################### Functions ###########################
#
def save_reservation(request, id=None):
	instance = None

	if id is not None: # if updating an existing reservation
		instance = get_object_or_404(Reservation, pk=id)

	form = ReservationForm(
		{
			'user': request.POST['user'],
			'project': request.POST['project'],
			'start_date': request.POST['start-date'],				
			'end_date': request.POST['end-date'],
			'items': request.POST.getlist('items'),
			'crew': request.POST['crew'],
			'comment': request.POST['comment']
		},
		instance=instance		
	)

	if form.is_valid():			
		# Save to database
		reservation = form.save()

		# Send email for new reservations only
		if instance is None:
			send_email(request, reservation.pk)

		return form, reservation

	return form, instance

def delete_reservation(id=None):
	if id is not None:
		try:
			# Get reservation
			reservation = Reservation.objects.get(pk=id)
			
			# Delete reservation
			reservation.delete()

			return reservation
		except ObjectDoesNotExist:
			return HttpResponse("Reservation not found!")

def send_email(request, id=None):
	if request.POST.get('reserve'):
		if id is not None:
			# Get reservation details
			reservation = Reservation.objects.select_related('user').prefetch_related('items').get(pk=id)

			warning = ''

			# Check reservation time
			time_span = reservation.end_date - reservation.start_date

			# Convert to local time zone
			local_start_date = timezone.localtime(reservation.start_date)
			local_end_date = timezone.localtime(reservation.end_date)

			if local_start_date.day != local_end_date.day:
				warning = 'This reservation request spans overnight.'
			elif time_span.total_seconds() > timedelta(hours=6).seconds:
				warning = 'This reservation request is for %s hours.' % int(time_span.total_seconds() / timedelta(hours=1).seconds)

			# Construct message			
			message = (Reservation.EMAIL_ADMIN_RESERVATION_APPROVAL % (reservation.user, reservation.project,
				local_start_date.strftime("%m-%d-%Y %I:%M %p"), local_end_date.strftime("%m-%d-%Y %I:%M %p"),
				warning, "\n".join(str(item) for item in reservation.items.all()), reservation.crew, reservation.comment, reservation.id))

			# Construct html message			
			message_html = (Reservation.EMAIL_ADMIN_RESERVATION_APPROVAL_HTML % (reservation.user, reservation.project,
				local_start_date.strftime("%m-%d-%Y %I:%M %p"), local_end_date.strftime("%m-%d-%Y %I:%M %p"),
				warning, "</li>".join('<li>' + str(item) for item in reservation.items.all()), reservation.crew, reservation.comment, reservation.id))

			# Send email
			send_mail('New Staff Equipment Reservation', message, 'noreply@asicsulb.org', User.ERS_ADMINS, html_message=message_html)

			return True

	elif request.POST.get('approve'):
		if id is not None:
			# Get reservation details
			reservation = Reservation.objects.select_related('user__department').prefetch_related('items').get(pk=id)

			# Convert to local time zone
			local_start_date = timezone.localtime(reservation.start_date)
			local_end_date = timezone.localtime(reservation.end_date)

			message = ''
			
			if request.POST.get('message'):
				message = 'The following message was included: ' + request.POST.get('message')

			# Construct message
			message_for_producer = (Reservation.EMAIL_STAFF_APPROVAL % (reservation.user, reservation.project,
				local_start_date.strftime("%m-%d-%Y %I:%M %p"), local_end_date.strftime("%m-%d-%Y %I:%M %p"),
				"\n".join(str(item) for item in reservation.items.all()), reservation.crew, message))

			# Send approval to supervisor as well
			supervisor = None
			if reservation.user.department.name == 'ACVP':
				supervisor = User.ERS_ACVP_SUP
			elif reservation.user.department.name == 'CBTV':
				supervisor = User.ERS_CBTV_SUP
			
			# Send email
			send_mail('Equipment Reservation Approved', message_for_producer, 'noreply@asicsulb.org', [reservation.user.email, supervisor])

			return True

	elif request.POST.get('decline') or request.POST.get('delete'):
		if id is not None:
			# Get reservation details
			try:
				reservation = Reservation.objects.select_related('user').get(pk=id)
			except ObjectDoesNotExist:				
				return False

			# Convert to local time zone
			local_start_date = timezone.localtime(reservation.start_date)
			local_end_date = timezone.localtime(reservation.end_date)

			if request.POST.get('message'):
				reason = 'The following reason was given: ' + request.POST.get('message')
			else:
				reason = 'No reason was given.'

			# Construct message
			message_for_producer = (Reservation.EMAIL_STAFF_DECLINE % (reservation.user, reservation.project,
				local_start_date.strftime("%m-%d-%Y %I:%M %p"), local_end_date.strftime("%m-%d-%Y %I:%M %p"), reason))

			# Send email
			send_mail('Equipment Reservation Declined or Canceled', message_for_producer, 'noreply@asicsulb.org', [reservation.user.email])

			return True
	
	return False