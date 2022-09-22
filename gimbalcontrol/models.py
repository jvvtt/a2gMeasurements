from django.db import models
from django.urls import reverse
import uuid
import datetime
from django.utils import timezone
#from GimbalRS2 import GimbalRS2
from a2gmeasurements import GimbalRS2, GpsSignaling
import can
import threading
  
class PcanInstance(models.Model):
    bus_is_active = models.BooleanField(default=False)
    
    gc = GimbalRS2()    

class SeptentrioGpsInstance(models.Model):
    gps_is_active = models.BooleanField(default=False)
    
    gps = GpsSignaling(1)

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
    
class GpsDataBase(models.Model):
    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)
    gps_time_tag = models.DateTimeField('GPS Time Tag')
    
    # More gps info to be entered here
    
    def __str__(self):
        return  'LAT: %.7f, LON: %.7f' % (self.latitude, self.longitude)
    
class AutomaticMove(models.Model):
    # It is a replica of the ManualMove class, but it is created to save the automatic gimbal movements in another database TABLE.
    # We could add another field to the ManualMove class to differentiate between a manual movement and an automatic one,
    # but then the name of the class (ManualMove) would be not crystal-clear
                
    yaw = models.IntegerField(default=0, help_text='Enter yaw integer')
    roll = models.IntegerField(default=0, help_text='Enter roll integer')
    pitch = models.IntegerField(default=0, help_text='Enter pitch integer')
    
    time_tag = models.DateTimeField('Time tag')
    
    
class Presets(models.Model):
    3