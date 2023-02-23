from django.db import models

class Participant(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length = 254) 
    availabilities = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name

    def is_available(self, start_time, end_time):
        if self.availabilities==None:
            return True
        for availability in self.availabilities.values():
            if start_time < availability['end_time'] and end_time > availability['start_time']:
                return False
        return True

    def set_availability(self, start_time, end_time):
        self.availabilities[str(start_time)] = {'start_time': str(start_time), 'end_time': str(end_time)}
        self.save()

class Interview(models.Model):
    id=models.AutoField(primary_key=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    participants = models.ManyToManyField(Participant)

    def __str__(self):
        return f'Interview {self.id} ({self.start_time} - {self.end_time}'