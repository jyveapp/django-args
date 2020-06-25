django-args
===========

``django-args`` is the `Django <https://www.djangoproject.com/>`__
wrapper on `python-args <https://github.com/jyveapp/python-args>`__.

``python-args`` provides the ability to decorate functions with validators,
context, and default value processors. ``django-args`` takes this a
step further, allowing any function decorated with ``python-args`` to
seamlessly integrate with Django form views and form wizards.

Quick Start
~~~~~~~~~~~

``django-args`` provides the following core views, which we cover in-depth
in the ref:`django-args tutorial <tutorial>`__:

1. `djarg.views.FormView` - For constructing a form view on a ``python-args``
   function.
2. `djarg.views.WizardView` - For constructing a
   `django-formtools <https://django-formtools.readthedocs.io/en/latest/>`__
   form wizard on a ``python-args`` function.

Each one of these views has additional extensions for easily constructing
views on top of models. Here are a few:

1. `djarg.views.ObjectFormView` - For form views on a single object.
2. `djarg.views.ObjectsFormView` - For form views on multiple objects.
3. `djarg.views.ObjectWizardView` - For wizards on a single object.
4. `djarg.views.ObjectsWizardView` - For wizards on multiple objects.

``django-args`` also provides several utilities to facilitate Django integration
with ``python-args`` functions:

1. The `djarg.qset` utility is a ``python-args`` lazy loader and allows users
   to lazily load a queryset for a function.
2. The `djarg.views.SuccessMessageMixin` mimics Django's ``SuccessMessageMixin``
   for form views, but it is compatible with all ``django-args`` views.

In order to get started, first go through the
:ref:`installation instructions <installation>`. Then head on to the
:ref:`django-args tutorial <tutorial>`.
