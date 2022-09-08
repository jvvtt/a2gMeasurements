from django.apps import AppConfig
import time
from GimbalRS2 import GimbalRS2
import threading
        
class GimbalcontrolConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gimbalcontrol'
            