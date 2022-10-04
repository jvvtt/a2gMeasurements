from django.shortcuts import render, get_object_or_404
from .models import ManualMove, AutomaticMove, PcanInstance, SeptentrioGpsInstance, GpsDataBase
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.views import generic
from .forms import GimbalSetPositionForm
import datetime, can, time, threading
import numpy as np

def index(request):
    
    # When opening the index page, instances of all devices must be retrieved.
    
    # There should be only 1 pcan instance, so either there is one object in th db or not
    try:
        pcan = PcanInstance.objects.all().last()

        # This variable is to remember if can bus is active, as 'bus_is_active' flag is set when creating an PcanInstance object only
        # means it is retrieved each time we point to the index page
        pcan_is_active = pcan.bus_is_active
        
        septentrio = SeptentrioGpsInstance.objects.all.last()
        
        septentrio_is_active = septentrio.gps_is_active
        
    # If there is no object, then pcan has not been initialized
    except:
        pcan_is_active = False
        
        septentrio_is_active = False
        
      # If this is a POST request then process the Form data
    if request.method == 'POST':
        
        if 'start_button' in request.POST:     
            # Start gimbal thread       
            pcan_instance = PcanInstance()
            pcan_instance.gc.start_thread_gimbal()   
            pcan_instance.save()
            
            pcan_is_active = True
            
            # Start gps thread
            gps_instance = SeptentrioGpsInstance()
            gps_instance.gps.serial_connect()
            gps_instance.gps.start_thread_serial()
            gps_instance.save()
            
            septentrio_is_active = True
            gps_instance.gps.start_gps_data_retrieval()
            
            
        elif 'stop_button' in request.POST:
            pcan.gc.stop_thread_gimbal()
            
            # A delay is required
            time.sleep(0.01) 
       
            pcan.gc.actual_bus.shutdown()
            pcan.delete()
            
            pcan_is_active = False
            
            return HttpResponseRedirect( reverse('index') )

    # If this is a GET (or any other method) create the default form.
    #else:
        #pcan_is_active = False

    return render(request, 'index.html', context={'pcan_is_active':pcan_is_active})
    
def myManualViewView(request):
    
    # There should be only 1 pcan instance: either there is one pcan object in the model class or none
    try:
        pcan = PcanInstance.objects.all().last()
        
    # If there is no object, then pcan has not been initialized, and we redirect to the index page
    except:
        return render(request, 'index.html', context={'pcan_is_active':False})    
    
    # IMPORTANT NOTE: THERE MUST BE AT LEAST ONE DEFAULT ENTRY IN THE DATABASE (i.e. THE 0,0,0 HOME POINT)
    #m_move = ManualMove.objects.get(id=1)
    m_move = ManualMove.objects.order_by('-time_tag')[:1]
    
    # If this is a POST request then process the Form data
    if request.method == 'POST':
        
        # Create a form instance and populate it with data from the request (binding):
        form = GimbalSetPositionForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            
            if 'set-button' in request.POST:
                # process the data in form.cleaned_data as required
                
                if form.cleaned_data['type_movement'] == 'abs':
                    yw = form.cleaned_data['yaw_angle']
                    rll = form.cleaned_data['roll_angle']
                    ptch = form.cleaned_data['pitch_angle']
                    
                elif form.cleaned_data['type_movement'] == 'rel':
                    pcan.gc.request_current_position()
                    
                    time.sleep(0.02)
                                        
                    yw = pcan.gc.yaw*10 + form.cleaned_data['yaw_angle']
                    yw = int(yw)
                    
                    if yw > 1800:
                        yw = yw - 3600
                    if yw < -1800:
                        yw = yw + 3600
                    
                    rll = pcan.gc.roll*10 + form.cleaned_data['roll_angle']
                    rll = int(rll)
                    
                    if rll > 1800:
                        rll = rll - 3600
                    if rll < -1800:
                        rll = rll + 3600
                    
                    ptch = pcan.gc.pitch*10 + form.cleaned_data['pitch_angle']
                    ptch = int(ptch)
                    
                    if ptch > 1800:
                        ptch = ptch - 3600
                    if ptch < -1800:
                        ptch = ptch + 3600
                
                #manual_move = ManualMove(yaw=form.cleaned_data['yaw_angle'], roll=form.cleaned_data['roll_angle'], pitch=form.cleaned_data['pitch_angle'], time_tag=datetime.datetime.now())
                #pcan.gc.setPosControl(form.cleaned_data['yaw_angle'], 
                #                    roll=form.cleaned_data['roll_angle'], 
                #                    pitch=form.cleaned_data['pitch_angle'], 
                #                    time_for_action=0x1A)
                
                manual_move = ManualMove(yaw=yw, roll=rll, pitch=ptch, time_tag=datetime.datetime.now(), type_movement=form.cleaned_data['type_movement'])
                manual_move.save()

                pcan.gc.setPosControl(yw, 
                                    roll=rll, 
                                    pitch=ptch, 
                                    time_for_action=0x1A)
                
                # redirect to a new URL:
                return HttpResponseRedirect( reverse('manual-move') )
            
            elif 'get-button' in request.POST:
                pcan.gc.request_current_position()
                
                # Block a bit of time, so that the yaw, roll, and pitch position is updated in the GimbalRS2 object
                time.sleep(0.02)
                actual_position = {'YAW': str(pcan.gc.yaw), 'ROLL': str(pcan.gc.roll), 'PITCH': str(pcan.gc.pitch)}
                
                return render(request, 'manual_move.html', context={'form': form, 'last_yaw': m_move[0].yaw, 'last_roll': m_move[0].roll, 'last_pitch': m_move[0].pitch, 'last_date': m_move[0].time_tag, 'actual_position':actual_position})
            
        else:
            return Http404("Invalid form")

    # If this is a GET (or any other method) create the default form.
    else:
        form = GimbalSetPositionForm(initial={'yaw_angle': 0, 'roll_angle': 0, 'pitch_angle': 0, 'type_movement': m_move[0].type_movement})

    return render(request, 'manual_move.html', context={'form': form, 'last_yaw': m_move[0].yaw, 'last_roll': m_move[0].roll, 'last_pitch': m_move[0].pitch, 'last_date': m_move[0].time_tag})
