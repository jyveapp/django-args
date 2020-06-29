from contextlib import ExitStack as does_not_raise

import arg
import ddf
import django.contrib.auth.models as auth_models
import pytest

import djarg.utils


def test_attach_select_for_update():
    """
    Verifies that _attached_select_for_update behaves as expected on
    a queryset
    """
    qset = auth_models.User.objects.all()

    # A select_for_update should never be attached to a function
    # not running under python-args
    new_qset = djarg.utils._attach_select_for_update(qset, None)
    assert not new_qset.query.select_for_update

    new_qset = djarg.utils._attach_select_for_update(qset, True)
    assert not new_qset.query.select_for_update

    # Test verious scenarios of properly adding a select_for_update
    @arg.defaults(
        qset=djarg.qset('qset', model=auth_models.User, select_for_update=True)
    )
    def no_args_select_for_update(qset):
        return qset

    assert no_args_select_for_update(qset).query.select_for_update

    @arg.defaults(
        qset=djarg.qset(
            'qset', model=auth_models.User, select_for_update=['self']
        )
    )
    def of_arg_select_for_update(qset):
        return qset

    assert of_arg_select_for_update(qset).query.select_for_update
    assert of_arg_select_for_update(qset).query.select_for_update_of == [
        'self'
    ]

    @arg.defaults(
        qset=djarg.qset(
            'qset',
            model=auth_models.User,
            select_for_update={'of': ['self'], 'skip_locked': True},
        )
    )
    def kwarg_select_for_update(qset):
        return qset

    assert kwarg_select_for_update(qset).query.select_for_update
    assert kwarg_select_for_update(qset).query.select_for_update_of == ['self']
    assert kwarg_select_for_update(qset).query.select_for_update_skip_locked


@pytest.mark.django_db
@pytest.mark.parametrize(
    'qset_kwargs, expected_error',
    [
        ({'model': auth_models.User}, does_not_raise()),
        ({'qset': auth_models.User.objects.all()}, does_not_raise()),
        ({}, pytest.raises(ValueError, match='provide model or qset')),
    ],
)
def test_qset(qset_kwargs, expected_error):
    """Tests the djarg.qset utility for coercing querysets"""

    with expected_error:

        @arg.defaults(
            users=djarg.qset('users', **qset_kwargs).prefetch_related('groups')
        )
        def get_user_groups(users):
            return {group for user in users for group in user.groups.all()}

        users = ddf.G(auth_models.User, n=3)
        groups = ddf.G(auth_models.Group, n=3)

        users[0].groups.add(groups[0], groups[1])
        users[1].groups.add(groups[1], groups[2])
        users[2].groups.add(groups[2])

        assert get_user_groups(None) == set()
        assert get_user_groups([]) == set()
        assert get_user_groups([users[0].id]) == {groups[0], groups[1]}
        assert get_user_groups([users[0].id, users[1].id]) == set(groups)
        assert get_user_groups([users[0], users[1]]) == set(groups)
        assert get_user_groups(users[0]) == {groups[0], groups[1]}
        assert get_user_groups(
            auth_models.User.objects.filter(id=users[0].id)
        ) == {groups[0], groups[1]}
