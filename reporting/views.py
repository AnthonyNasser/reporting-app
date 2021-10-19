from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Prefetch
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from reporting.models import Report, Representative, Meeting, Committee

class AjaxResponseMixin(object):
	def form_invalid(self, form):
		response = super(AjaxResponseMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):
		current_reps = Representative.objects.none()
		current_coms = Committee.objects.none()

		# Check if updated
		updated = self.object

		# If updated, get current many-to-many relations
		if updated:
			if hasattr(self.object, 'representatives'):
				current_reps = self.object.representatives.all()
			elif hasattr(self.object, 'committees'):
				current_coms = self.object.committees.all()

		# Save/Update object
		response = super(AjaxResponseMixin, self).form_valid(form)

		# Check for representatives/committees in form
		if 'representatives[]' in form.data or current_reps:
			representative_list = form.data.getlist('representatives[]')
			reps = self.saveRepresentatives(current_reps, representative_list)

			# Send email to representatives about committee membership
			self.send_email([form.cleaned_data['name']], [r.email for r in reps])
		elif 'committees[]' in form.data or current_coms:
			committee_list = form.data.getlist('committees[]')
			coms = self.saveCommittees(current_coms, committee_list)

			# Send email to representative about committee memberships
			self.send_email([c.name for c in coms], [form.cleaned_data['email']])

		if self.request.is_ajax():
			data = {
				'pk': self.object.pk,
				'start_time': self.object.start_time,
				'end_time': self.object.end_time,
				'location': self.object.location,
				'schedule': self.object.schedule,
				'active': True if self.object.active else False,
				'committee': self.object.committee,
				'updated': True if updated else False
			}
			return JsonResponse(data)
		else:
			return response
	
	def saveRepresentatives(self, current_reps, representatives):
		"""
		Save selected representatives when creating/updating committees

		Args:
			current_reps: list of current representatives in this committee
			representatives: list of selected representatives in comittee form
		Returns:
			list: list of representatives that were newly added to this committee			
		"""

		new_reps = []

		reps = Representative.objects.in_bulk(representatives)

		for rep_id, rep in reps.items():
			# If rep is not currently a member of this committee, add it to new rep list
			if not current_reps.filter(pk=rep_id).exists():
				new_reps.append(rep)
		
		removed_reps = current_reps.exclude(id__in=reps.keys()).values_list('id', flat=True)

		# Remove representatives that are no longer members of this committee
		self.object.representatives.remove(*removed_reps)
		
		# Bulk add new representatives to committee
		self.object.representatives.add(*new_reps)

		return new_reps

	def saveCommittees(self, current_coms, committees):
		"""
		Save selected committees when creating/updating representatives

		Args:
			current_coms: list of current committees this representative belongs to
			committeess: list of selected committees in form		
		Returns:
			list: list of committees that were newly added to this representative
		"""

		new_coms = []

		coms = Committee.objects.in_bulk(committees)

		# Get committee ids
		for com_id, com in coms.items():
			if not current_coms.filter(pk=com_id).exists():
				new_coms.append(com)
		
		removed_coms = current_coms.exclude(id__in=coms.keys()).values_list('id', flat=True)
		
		# Remove committees from this representative
		self.object.committees.remove(*removed_coms)

		# Bulk add new committees to committee
		self.object.committees.add(*new_coms)

		return new_coms
	
	def send_email(self, committee_list, recipient_list):
		"""
		Send email to representatives about committee membership

		Args:
			committee_list: list of committees that recipient_list belongs to
			recipient_list: list of representatives that became members of committee_list
		"""

		text_email = ('Dear Committee Member,\n\nYou have been added to the following committees:\n{}\n\nPlease submit committee reports within 6 days at: '
					'https://asicsulb.org/apps/reporting/reports/add/.\n\nAdd the meeting times to your calendar so you don\'t forget! If you have any questions please reach out to me.\n\n'
					'From,\nEmely Lopez\nChief Academic Officer\nAssociated Students, Inc. CSULB\nOffice Location: USU 311\nEmail: Emely.Lopez-SA@csulb.edu')
		
		html_email = ('<p>Dear Committee Member,</p><p>You have been added to the following committees:</p><ul>{}</li></ul><p>Please submit committee reports within 6 days at: '
					'<a href="https://asicsulb.org/apps/reporting/reports/add/" target="_blank">https://asicsulb.org/apps/reporting/reports/add/</a>.</p>'
					'<p>Add the meeting times to your calendar so you don\'t forget! If you have any questions please reach out to me.</p>'
					'<p>From,<br />Emely Lopez<br /><br />Chief Academic Officer<br />Associated Students, Inc. CSULB<br />Office Location: USU 311<br />'
					'Email: <a href="mailto:Emely.Lopez-SA@csulb.edu">Emely.Lopez-SA@csulb.edu</a></p>')
		
		message = text_email.format("\n".join(item for item in committee_list))

		# Construct html message
		message_html = html_email.format("</li>".join('<li>' + item for item in committee_list))
		
		# Send emails
		send_mail('Welcome', message, 'noreply@asicsulb.org', recipient_list, html_message=message_html)

class ReportCreate(SuccessMessageMixin, CreateView):
	model = Report
	template_name = 'reporting/base_submission.html'
	fields = ['purpose', 'business', 'description', 'recommendation', 'meeting', 'representative']
	# Redirect back to form
	success_url = reverse_lazy('reporting:report-add')
	success_message = "Report was submitted successfully for %(representative)s"

	def get_context_data(self, **kwargs):
		context = super(ReportCreate, self).get_context_data(**kwargs)

		reps = []

		# Get all rep meetings and reports
		rep_meetings_and_reports = Representative.objects.prefetch_related(
			Prefetch(
				'committees',
				queryset=Committee.objects.prefetch_related('meetings').exclude(meetings__isnull=True)
			),
			'rep_reports'
		)

		# Add meetings that have no report by representative
		for rep in rep_meetings_and_reports:
			reps.append({
				'id': rep.id,
				'name': rep.full_name,
				'email': rep.email,
				'title': rep.title,
				'committees': [
					{
						'id': c.id,
						'name': c.name,
						'meetings': [
							{
								'id': m.id,
								'start_time': m.start_time.strftime('%Y-%m-%d %H:%M'),
								'end_time': m.end_time.strftime('%Y-%m-%d %H:%M'),
								'location': m.location
							} for m in c.meetings.all() if (m.id, rep.id) not in [(r.meeting_id, r.representative_id) for r in rep.rep_reports.all()]
						]
					} for c in rep.committees.all()
				]
			})
		
		context['reps'] = list(reps)
		return context

@method_decorator(login_required, name='dispatch')
class ReportDetailView(DetailView):
	queryset = Report.objects.select_related('representative', 'meeting__committee')
	template_name = 'reporting/base_submission.html'
	context_object_name = 'report'

@method_decorator(login_required, name='dispatch')
class ReportListView(ListView):
	queryset = Report.objects.select_related('representative', 'meeting__committee').order_by('-submitted_on')
	template_name = 'reporting/base_report_list.html'
	context_object_name = 'report_list'
	paginate_by = 25

@method_decorator(login_required, name='dispatch')
class ReportDeleteView(DeleteView):
	model = Report
	success_url = reverse_lazy('reporting:report-list')

@method_decorator(login_required, name='dispatch')
class CommitteeCreate(AjaxResponseMixin, CreateView):
	model = Committee
	fields = ['name', 'num_of_seats', 'contact', 'committee_type']
	success_url = reverse_lazy('reporting:dashboard')

@method_decorator(login_required, name='dispatch')
class CommitteeUpdate(AjaxResponseMixin, UpdateView):
	model = Committee
	fields = ['name', 'num_of_seats', 'contact', 'committee_type']
	success_url = reverse_lazy('reporting:dashboard')

@method_decorator(login_required, name='dispatch')
class CommitteeDelete(DeleteView):
	model = Committee
	success_url = reverse_lazy('reporting:dashboard')

@method_decorator(login_required, name='dispatch')
class RepresentativeCreate(AjaxResponseMixin, CreateView):
	model = Representative
	fields = ['first_name', 'last_name', 'email', 'title', 'chair_email', 'committees']
	success_url = reverse_lazy('reporting:dashboard')

@method_decorator(login_required, name='dispatch')
class RepresentativeUpdate(AjaxResponseMixin, UpdateView):
	model = Representative
	fields = ['first_name', 'last_name', 'email', 'title', 'chair_email', 'committees']
	success_url = reverse_lazy('reporting:dashboard')

@method_decorator(login_required, name='dispatch')
class RepresentativeDelete(DeleteView):
	model = Representative
	success_url = reverse_lazy('reporting:dashboard')

@method_decorator(login_required, name='dispatch')
class MeetingCreate(AjaxResponseMixin, CreateView):
	model = Meeting
	fields = ['start_time', 'end_time', 'location', 'schedule', 'active', 'committee']
	success_url = reverse_lazy('reporting:dashboard')

@method_decorator(login_required, name='dispatch')
class MeetingUpdate(AjaxResponseMixin, UpdateView):
	model = Meeting
	fields = ['start_time', 'end_time', 'location', 'schedule', 'active', 'committee']
	success_url = reverse_lazy('reporting:dashboard')

@method_decorator(login_required, name='dispatch')
class MeetingDelete(DeleteView):
	model = Meeting
	success_url = reverse_lazy('reporting:dashboard')

@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
	template_name = 'reporting/base_dashboard.html'

	def get_context_data(self, **kwargs):
		context = super(DashboardView, self).get_context_data(**kwargs)
		context['representatives'] =  Representative.objects.prefetch_related('committees')
		context['committees'] = Committee.objects.prefetch_related('representatives')
		context['meetings'] = Meeting.objects.select_related('committee')
		return context
	
	def get(self, request, *args, **kwargs):
		if request.user.is_staff:
			context = self.get_context_data(**kwargs)
			return self.render_to_response(context)
		else:
			return HttpResponseRedirect(reverse('reporting:report-add'))