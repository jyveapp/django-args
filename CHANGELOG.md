# Changelog
## 1.0.1 (2020-06-28)
### Trivial
  - Added more information to the README. [Wes Kendall, c277f62]

## 1.0.0 (2020-06-25)
### Api-Break
  - Initial release of django-args [Wes Kendall, 625004d]

    The first version of django-args provides several fundamental Django
    wrappers for python-args, including:

    1. ``djarg.views.FormView``: For constructing form views on ``python-args``
       functions.
    2. ``djarg.views.FormWizardView``: For constructing form wizards on ``python-args``
       functions.
    3. ``djarg.form.Field``: For fields that can be dynamically bound to forms.

    Along with these core views, ``django-args`` provides several object-based
    views for working with single and multiple objects.

    1. ``djarg.views.ObjectFormView``: For constructing form views on a single
       object with ``python-args`` functions.
    2. ``djarg.views.ObjectsFormView``: For constructing form views on multiple
       objects with ``python-args`` functions.
    3. ``djarg.views.ObjectWizardView``: For constructing wizards on a single
       object with ``python-args`` functions.
    4. ``djarg.views.ObjectsWizardView``: For constructing wizards on multiple
       objects with ``python-args`` functions.

    The first version of ``django-args`` also comes with the following
    utilities:

    1. ``djarg.qset`` - Similar to other lazy ``python-args`` loaders, a lazy
       loader for loading querysets as default arguments to ``python-args``
       functions.
    2. ``djarg.views.SuccessMessageMixin`` - Similar to Django's
       SuccessMessageMixin, allows views to automatically add a success message
       upon successful completion.

