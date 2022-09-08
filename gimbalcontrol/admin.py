from django.contrib import admin
from .models import ManualMove, AutomaticMove, Presets

admin.site.register(ManualMove)
admin.site.register(AutomaticMove)
admin.site.register(Presets)



