from django.db import models
from django.urls import reverse
import uuid
import datetime
from django.utils import timezone
#from GimbalRS2 import GimbalRS2
from a2gmeasurements import GimbalRS2
import can
import threading

class MyClass():
    def __init__(self, name, lastname):
        self.name = name
        self.lastname = lastname
        
    def dummy1(self):
        return self.name + str(2*7)
    
    def dummy2(self):
        return self.lastname + str(2*10)
    
class PcanInstance(models.Model):
    bus_is_active = models.BooleanField(default=False)
    
    gc = GimbalRS2()    

class ManualMove(models.Model):
    # Campos
    TYPES_MOVEMENT = (('abs', 'Absolute'),('rel', 'Relative'))
    
    type_movement = models.CharField(max_length= 20,choices=TYPES_MOVEMENT, default='abs')
    
    yaw = models.IntegerField(default=0, help_text='Enter yaw integer')
    roll = models.IntegerField(default=0, help_text='Enter roll integer')
    pitch = models.IntegerField(default=0, help_text='Enter pitch integer')
    
    time_tag = models.DateTimeField('Time tag')
    
    # a = timezone.now()
    # b = a.strftime("%d/%m/%Y - %H:%M:%S:%f")
    
    #speed = models.IntegerField(default=0, help_text='Enter pitch integer')
    #type_movement = models.IntegerField(default=0)
    
    # Métodos
    def get_absolute_url(self):
         """
        
         """
         return reverse('model-detail-view', args=[str(self.id)])

    def __str__(self):
        """
            Wht to show in the db manager entry
        """
        return 'YAW: %d, ROLL: %d, PITCH: %d' % (self.yaw, self.roll, self.pitch)
    

class AutomaticMove(models.Model):
    2
    
class Presets(models.Model):
    3