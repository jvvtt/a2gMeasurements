from django import forms

from django.core.exceptions import ValidationError
import datetime #for checking renewal date range.

class GimbalSetPositionForm(forms.Form):
    TYPES_MOVEMENT = (('abs', 'Absolute'),('rel', 'Relative'))
    
    type_movement = forms.ChoiceField(label='Choose type of movement', choices=TYPES_MOVEMENT)
    
    yaw_angle = forms.IntegerField(label='Yaw', help_text="Value between -1800 and 1800")
    roll_angle = forms.IntegerField(label='Roll', help_text="Value between -1800 and 1800")
    pitch_angle = forms.IntegerField(label='Pitch', help_text="Value between -1800 and 1800")

    yaw_limits = {'min_ang': -1800, 'max_ang': 1800}
    roll_limits = {'min_ang': -1800, 'max_ang': 1800}
    pitch_limits = {'min_ang': -1800, 'max_ang': 1800}
    
    def clean_yaw_angle(self):
        data = self.cleaned_data['yaw_angle']
        
        if data < self.yaw_limits['min_ang']:
            raise ValidationError('Invalid value')

        if data > self.yaw_limits['max_ang']:
            raise ValidationError('Invalid value')
        
        return data
    
    def clean_roll_angle(self):
        data = self.cleaned_data['roll_angle']
        
        if data < self.roll_limits['min_ang']:
            raise ValidationError('Invalid value')

        if data > self.roll_limits['max_ang']:
            raise ValidationError('Invalid value')
        
        return data
    
    def clean_pitch_angle(self):
        data = self.cleaned_data['pitch_angle']
        
        if data < self.pitch_limits['min_ang']:
            raise ValidationError('Invalid value')

        if data > self.pitch_limits['max_ang']:
            raise ValidationError('Invalid value')
        
        return data