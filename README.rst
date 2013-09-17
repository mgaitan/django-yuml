====================
Django Yuml
====================

Generates YUML class diagram for you django project or specified apps in project

http://yuml.me

Installation
================
#. Add the `django_yuml` directory to your Python path.

#. Add `django_yuml` to your `INSTALLED_APPS` setting so Django can find it.


Examples
================

#. python manage.py yuml yourapp yoursecondapp -s scruffy -p 75 -o test.png

#. python manage.py yuml justoneapp -s scruffy -o test.pdf

#. generate whole project yuml
   
   python manage.py yuml -a -o test.jpg

#. python manage.py yuml auth contenttypes sessions admin -o test.pdf

This is how looks generated diagram for command: 

#. python manage.py yuml auth contenttypes sessions sites messages admin -s scruffy -p 200 -o example.jpg

  http://www.gang.lt/example.jpg
