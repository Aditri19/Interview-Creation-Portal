from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Interview, Participant

I_CLASS = 'w-full py-4 px-6 rounded-xl border'
class InterviewForm(forms.ModelForm):
    participants = forms.ModelMultipleChoiceField(
        queryset=Participant.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    class Meta:
        model = Interview
        fields = ['start_time', 'end_time', 'participants']


    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        participants = cleaned_data.get('participants')

        if start_time and end_time and start_time >= end_time:
            raise ValidationError(
                _("End time should be greater than start time")
            )

        if participants:
            for participant in participants:
                if Interview.objects.filter(participants=participant).exclude(pk=self.instance.pk).filter(start_time__lt=end_time, end_time__gt=start_time).exists():
                    raise forms.ValidationError(f"{participant} is not available during scheduled time.")

        # Check if number of participants is greater than or equal to 2
        if participants and len(participants) < 2:
            raise forms.ValidationError("Please select at least two participants.")



class EditInterviewForm(forms.ModelForm):
    participants = forms.ModelMultipleChoiceField(queryset=Participant.objects.all())
    start_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    end_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['participants'].widget.attrs.update({'class': 'form-control select2', 'multiple': 'multiple'})
        self.fields['start_time'].input_formats = ('%Y-%m-%dT%H:%M',)
        self.fields['end_time'].input_formats = ('%Y-%m-%dT%H:%M',)
    
    class Meta:
        model = Interview
        fields = ['participants', 'start_time', 'end_time']

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        participants = cleaned_data.get('participants')

        for participant in participants:
            # Check if the participant has any other interview scheduled during the given time slot
            if Interview.objects.filter(participants=participant, start_time__lt=end_time, end_time__gt=start_time).exclude(pk=self.instance.pk).exists():
                self.add_error('participants', f'{participant} is not available during the scheduled time')
        
        if len(participants) < 2:
            self.add_error('participants', 'Select at least 2 participants')
            
        # delete existing time slots for the participants and save again
        for participant in participants:
            interview = Interview.objects.filter(participants=participant).exclude(pk=self.instance.pk).first()
            if interview:
                interview.start_time = None
                interview.end_time = None
                interview.save()
                
            interview = Interview.objects.create(participants=participant, start_time=start_time, end_time=end_time)

        return cleaned_data
