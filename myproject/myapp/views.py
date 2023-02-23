from django.shortcuts import render, get_object_or_404, redirect
from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from .models import Participant, Interview
from django.utils import timezone
from .forms import InterviewForm
from django.core.mail import send_mail

def create_interview(request):
    if request.method == 'POST':
        # Retrieve form data
        start_time = request.POST['start_time'] 
        end_time = request.POST['end_time']
        participants = request.POST.getlist('participants[]')
        print(start_time, end_time, participants)
        # Validate form data
        errors = []
        if start_time > end_time:
            errors.append('The interview time does not exist')
        elif len(participants) < 2:
            errors.append('At least two participants are required')
        else:
            
            for participant_id in participants:
                participant = Participant.objects.get(pk=participant_id)
                if participant.is_available(start_time, end_time):
                    participant.set_availability(start_time, end_time)
                else:
                    errors.append(f'{participant.name} is not available during the scheduled time')

        # If there are no errors, create the interview and redirect to the interviews list page
        if not errors:
            try:
                interview = Interview.objects.create(start_time=start_time, end_time=end_time)
                interview.participants.add(*participants)
                interview.save()
                return HttpResponseRedirect(reverse('interviews_list'))
            except IntegrityError:
                errors.append('Interview with the same participants and scheduled time already exists')

        # If there are errors, render the create interview page with error messages
        context = {'participants': Participant.objects.all(), 'errors': errors}
        return render(request, 'create_interview.html', context)

    # If the request method is GET, render the create interview page with empty form
    context = {'participants': Participant.objects.all()}
    return render(request, 'create_interview.html', context)


def interviews_list(request):
    upcoming_interviews = Interview.objects.filter(start_time__gte=timezone.now()).order_by('start_time')
    context = {'interviews': upcoming_interviews}
    return render(request, 'interviews_list.html', context)

def edit_interview(request, interview_id):
    interview = get_object_or_404(Interview, pk=interview_id)
    if request.method == 'POST':
        form = InterviewForm(request.POST, instance=interview)
        if form.is_valid():
            # check if participants are available during scheduled time
            if not form.clean():
                form.add_error(None, 'One or more participants are not available during the scheduled time.')
            else:
                interview = form.save()
                participants = form.cleaned_data['participants']
                start_time = form.cleaned_data['start_time']
                end_time = form.cleaned_data['end_time']
                send_emails(interview, participants, start_time, end_time, 'modified')
                return redirect(reverse('interviews_list'))
    else:
        form = InterviewForm(instance=interview)
    return render(request, 'edit_interview.html', {'form': form, 'interview_id': interview_id})


def send_emails(interview, participants, start_time, end_time, action):
    subject = f'Interview {action} - {interview}'
    message = f'The interview {interview} has been {action}.\n'
    message += f'The interview is scheduled from {start_time} to {end_time}.\n'
    message += f'Please make sure you are available at this time.\n'
    from_email = 'admin@example.com' # replace with your own email address or use settings.py
    recipient_list = [participant.email for participant in participants]
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)