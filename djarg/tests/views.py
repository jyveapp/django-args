"""
Views and forms used in integration tests for django-args
"""
import contextlib

import arg
from django import forms
from django.contrib.auth.models import User
from django.core import exceptions

import djarg.forms
import djarg.views


###
# Form view test setup
###


def check_username(user):
    if user.username.startswith('bad'):
        raise ValueError(f'Bad username')


def granter_must_be_superuser_and_staff(granter):
    if not granter.is_superuser or not granter.is_staff:
        raise ValueError(f'Granter must be superuser and staff.')


def granter_cant_be_user(granter, user):
    if user == granter:
        raise ValueError('The granter cannot be the user being granted.')


def validate_source(source):
    if source == 'BAD':
        raise exceptions.ValidationError('bad source name used')


@arg.defaults(source=arg.val('source').upper())
@arg.validators(
    granter_must_be_superuser_and_staff,
    granter_cant_be_user,
    validate_source,
    check_username,
)
def grant_staff_access(user, granter, is_staff, source):
    if user.username == 'run_error':
        raise RuntimeError('Test runtime error!')

    user.is_staff = is_staff
    user.save()


class GrantAccessForm(forms.Form):
    user = djarg.forms.Field(
        forms.ModelChoiceField,
        queryset=User.objects.all(),
        help_text=arg.val('help_text', default=''),
    )
    granter = forms.ModelChoiceField(queryset=User.objects.all())
    is_staff = djarg.forms.Field(forms.BooleanField, required=False)
    source = djarg.forms.Field(forms.CharField)


class GrantStaffView(djarg.views.FormView):
    func = grant_staff_access
    template_name = 'tests/grant_staff_access.html'
    form_class = GrantAccessForm
    success_url = '.'

    def get_default_args(self):
        return {**super().get_default_args(), **{'help_text': 'Help text'}}


###
# ObjectFormView test setup
###


class GrantAccessObjectForm(forms.Form):
    is_staff = djarg.forms.Field(forms.BooleanField, required=False)
    source = djarg.forms.Field(forms.CharField)


class GrantStaffObjectView(
    djarg.views.SuccessMessageMixin, djarg.views.ObjectFormView
):
    model = User
    func = arg.defaults(
        user=arg.val('object'), granter=arg.val('request').user
    )(grant_staff_access)
    template_name = 'tests/grant_staff_access.html'
    form_class = GrantAccessObjectForm
    success_url = '.'


###
# ObjectsFormView test setup
###


@contextlib.contextmanager
def raise_trapped_errors():
    error_collector = []
    yield error_collector

    if error_collector:
        raise exceptions.ValidationError(error_collector)


@contextlib.contextmanager
def trap_errors(error_collector):
    try:
        try:
            yield
        except Exception as exc:
            msg = f'{arg.call().parametrize_arg_val}: {exc}'
            raise exceptions.ValidationError(msg) from exc
    except Exception as exc:
        error_collector.append(exc)


class GrantStaffObjectsView(
    djarg.views.SuccessMessageMixin, djarg.views.ObjectsFormView
):
    model = User
    func = arg.s(
        arg.contexts(error_collector=raise_trapped_errors),
        arg.parametrize(user=arg.val('objects')),
        arg.contexts(trap_errors),
    )(grant_staff_access)
    template_name = 'tests/grant_staff_access.html'
    form_class = GrantAccessObjectForm
    success_url = '.'
    success_message = '{granter} successfully granted staff access to users.'

    def get_default_args(self):
        return {**super().get_default_args(), **{'granter': self.request.user}}


###
# SessionWizardView test setup
###


class GrantAccessStep1(forms.Form):
    user = djarg.forms.Field(
        forms.ModelChoiceField,
        queryset=User.objects.all(),
        help_text=arg.val('extra', default='hi'),
    )


class GrantAccessStep2(forms.Form):
    granter = djarg.forms.Field(
        forms.ModelChoiceField, queryset=User.objects.all()
    )


class GrantAccessStep3(forms.Form):
    is_staff = djarg.forms.Field(forms.BooleanField, required=False)


class GrantAccessStep4(forms.Form):
    source = djarg.forms.Field(
        forms.CharField,
        initial=arg.func(lambda is_staff: str(is_staff), 'staff_not_found'),
    )


class GrantStaffWizardView(djarg.views.SessionWizardView):
    func = grant_staff_access
    template_name = 'tests/grant_staff_access_wizard.html'
    form_list = [
        GrantAccessStep1,
        GrantAccessStep2,
        GrantAccessStep3,
        GrantAccessStep4,
    ]
    success_url = '.'

    def get_default_args(self):
        return {'extra': 'Help text'}


###
# Conditional SessionWizardView test setup
###


class GrantAccessUserGranterStaff(forms.Form):
    user = djarg.forms.Field(
        forms.ModelChoiceField,
        queryset=User.objects.all(),
        help_text=arg.val('extra', default='hi'),
    )
    granter = djarg.forms.Field(
        forms.ModelChoiceField, queryset=User.objects.all()
    )
    is_staff = djarg.forms.Field(forms.BooleanField, required=False)


class GrantAccessStepIsStaffTrue(forms.Form):
    source = djarg.forms.Field(forms.CharField, initial='Staff is true!')


class GrantAccessStepIsStaffFalse(forms.Form):
    source = djarg.forms.Field(forms.CharField, initial='Staff is false!')


class GrantStaffCondWizardView(djarg.views.SessionWizardView):
    func = grant_staff_access
    template_name = 'tests/grant_staff_access_wizard.html'
    form_list = [
        GrantAccessUserGranterStaff,
        GrantAccessStepIsStaffTrue,
        GrantAccessStepIsStaffFalse,
    ]
    condition_dict = {
        '0': lambda _: True,
        '1': arg.func(lambda is_staff, granter: is_staff),
        '2': arg.func(lambda is_staff: not is_staff),
    }
    success_url = '.'

    def get_default_args(self):
        return {**super().get_default_args(), **{'extra': 'Help text'}}


###
# SessionObjectWizardView test setup
###


class GrantStaffObjectWizardView(
    djarg.views.SuccessMessageMixin, djarg.views.SessionObjectWizardView
):
    model = User
    func = arg.defaults(user=arg.val('object'))(grant_staff_access)
    template_name = 'tests/grant_staff_access_wizard.html'
    form_list = [
        # We no longer need the first step. The user is provided by the
        # object view
        GrantAccessStep2,
        GrantAccessStep3,
        GrantAccessStep4,
    ]
    success_url = '.'

    def get_success_message(self, args, results):
        return f'Successfully granted access to {args["object"]}.'
