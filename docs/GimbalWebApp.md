## Web app

If it is of interest of the developer to migrate all the functionality done in PyQt5 (comprised in the files mentioned in section [Files in directory](MeasurementSystem.md#files-in-directory) ), to a web application, a *starting point* can be the web application developed to control the DJI Ronin RS2 gimbal. 

The web application was done using the Django framework, and its backbone (the directory structure shown as follows) can be further extended if it is required.

```
.
|- a2gmeasurements
 |- GimbalRS2WebApp
  |- gimbalcontrol  
   |- migrations
    |- __init__.py
    |- 0001_initial.py
   |- static
    |- css
     |- bootstrap.min.css
     |- styles.css
    |- js
     |- bootstrap.min.js
   |- templates
    |- automatic_move.html
    |- base_generic.html
    |- bs4_form.html
    |- index.html
    |- manual_move.html
   |- __init__.py
   |- admin.py
   |- apps.py
   |- forms.py
   |- models.py
   |- tests.py
   |- urls.py
   |- views.py
  |- webAppRS2
   |- __init__.py
   |- asgi.py
   |- settings.py
   |- urls.py
   |- wsgi.py
  | manage.py
```

Extending this web app mainly requires to modify the files ``forms.py``, ``models.py``, ``urls.py``, ``views.py`` and add the new html files (responsible for all the user interface functionality) under the ``templates`` directory, the new css files (if any) to the ``css`` directory, and the new javascript files (if any) to the ``js`` directory.