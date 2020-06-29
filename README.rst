django-args
###########

``django-args`` is the `Django <https://www.djangoproject.com/>`__
wrapper on `python-args <https://github.com/jyveapp/python-args>`__.

``python-args`` provides the ability to decorate functions with validators,
context, and default value processors. ``django-args`` takes this a
step further, allowing any function decorated with ``python-args`` to
seamlessly integrate with Django form views and form wizards.

For example, ``djarg.views.FormView`` automatically constructs a Django
``FormView`` on a python function and maps the form fields to the
function arguments. Assuming the function is wrapped with
``arg.validators``, ``django-args`` will seamlessly bind
the validators to the form. This same concept is extended to bulk
views and form views offered by ``django-args``.

Along with this, ``django-args`` also helps eliminate the burden
of passing around variables from views to forms for doing simple
initializations (choice fields, etc) and other boilerplate that
can become difficult to follow as a project grows.

Check out the `docs <https://django-args.readthedocs.io/>`__ for
more information on how you can use ``django-args`` for your
project. 

Documentation
=============

`View the django-args docs here
<https://django-args.readthedocs.io/>`_.

Installation
============

Install django-args with::

    pip3 install django-args

After this, add ``djarg`` to the ``INSTALLED_APPS``
setting of your Django project.

Contributing Guide
==================

For information on setting up django-args for development and
contributing changes, view `CONTRIBUTING.rst <CONTRIBUTING.rst>`_.

Primary Authors
===============

- @wesleykendall (Wes Kendall)
