from contextlib import ExitStack as does_not_raise

import arg
import ddf
import django.contrib.auth.models as auth_models
import pytest

import djarg


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
