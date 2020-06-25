import contextlib

import arg
from django import forms
from django.core.exceptions import ValidationError


@contextlib.contextmanager
def _only_raise_validation_error():
    """
    Re-raise everything as a Django ValidationError so that form cleaning
    works seamlessly.
    """
    try:
        yield
    except Exception as exc:
        if isinstance(exc, ValidationError):
            raise
        else:
            raise ValidationError(exc) from exc


def get_field_validator(func, field_label):
    """
    Given a field label and function, generate a form field validator
    from the function. It is assumed that the function is wrapped with
    ``python-args``.

    Django form fields need to raise ValidationErrors in order for
    errors to bubble up properly. This function wraps any
    validators for the field and re-raises ValidationErrors
    """

    def validate_field(val):
        with _only_raise_validation_error():
            func.partial.pre_func(**{field_label: val})

    return validate_field


def get_form_clean(func, form, default_args=None):
    """
    Returns a form clean method for the form, using any validators
    present on the ``python-args`` wrapped ``func``.
    """
    old_clean = form.clean
    default_args = default_args or {}

    def clean(*args, **kwargs):
        cleaned_data = old_clean(*args, **kwargs)

        with _only_raise_validation_error():
            func.partial.pre_func(**{**default_args, **cleaned_data})

        return cleaned_data

    return clean


def adapt(form, func, default_args=None):
    """
    Adapt a form to an python-args func, ensuring the form validation behaves
    seamlessly with function validation.

    Evaluate any djarg.form.Field classes that are fields of the form.

    Args:
        form (django.forms.Form): The Django form being adapted.
        func (function): A function decorated with ``python-args`` decorators.
        default_args (dict, default=None): A dictionary of any other default
            arguments that are used when calling the ``python-args`` function.
    """
    default_args = default_args or {}

    # Instantiate any lazy fields
    for label, field in form.fields.items():
        if isinstance(field, arg.Lazy):
            form.fields[label] = arg.load(
                field, **{**{'form': form}, **default_args}
            )

    # Attached additional form field validators
    for label, field in form.fields.items():
        field.validators.append(get_field_validator(func, label))

    # Attach additional form clean methods
    form.clean = get_form_clean(func, form, default_args=default_args)

    return form


class Field(arg.init, forms.Field):
    """A lazy ``python-args`` adapter to lazily load a Django form field.

    When declaring a form, a form field can be wrapped in the ``Field``
    object so that all attributes can be lazily loaded.

    Example:

        This is an example of lazily loading a form field so that we
        can dynamically fill out help text::

            class MyForm(forms.Form):
                field = Field(CharField, help_text=args.func(get_help_text))
    """

    def __init__(self, *args, **kwargs):
        arg.init.__init__(self, *args, **kwargs)
        forms.Field.__init__(self)

    def __getattribute__(self, name):
        return forms.Field.__getattribute__(self, name)
