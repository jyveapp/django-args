# Changelog
## 1.3.0 (2020-07-02)
### Feature
  - Add ``clean`` argument to turn off binding clean method in djarg.forms.adapt [Wes Kendall, 199ce5b]

    When adapting a form to a python-args function, one can disable adapting the
    clean method.

## 1.2.0 (2020-07-02)
### Feature
  - Allow ``.qset`` utility to lazy load querysets. [Wes Kendall, fa64670]

    The ``qset`` argument for bootstrapping the ``djarg.qset`` utility can
    now lazy load the querysets based on bound args.

## 1.1.0 (2020-06-29)
### Feature
  - Add a ``select_for_update`` option to ``djarg.qset`` [Wes Kendall, ab18034]

    The ``select_for_update`` option for ``djarg.qset`` can be used to dynmaically
    apply ``select_for_update`` on the queryset whenever one is not running in
    a partial ``python-args`` mode (such as validation-only)

## 1.0.1 (2020-06-29)
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

