import ddf
from django import urls
from django.contrib.auth.models import User
import pytest


@pytest.mark.django_db
def test_grant_staff_view(client):
    user = ddf.G(User, is_staff=True)
    granter = ddf.G(User, is_staff=False, is_superuser=True)
    url = urls.reverse('grant_staff_access')

    resp = client.get(url)
    html = resp.content.decode()
    # Verify the custom help text was rendered on our user field
    assert 'Help text' in html

    # Post no data. We should have a bunch of "field is required" errors
    resp = client.post(url, data={})
    assert resp.status_code == 200
    html = resp.content.decode()
    assert 'This field is required' in html

    # Post valid data that will exercise our validator logic
    resp = client.post(
        url,
        data={
            'user': user.id,
            'granter': granter.id,
            'is_staff': 'on',
            'source': 'source',
        },
    )
    assert resp.status_code == 200
    html = resp.content.decode()
    assert 'This field is required' not in html
    assert 'Granter must be superuser' in html

    granter.is_staff = True
    granter.save()
    resp = client.post(
        url,
        data={
            'user': granter.id,
            'granter': granter.id,
            'is_staff': 'on',
            'source': 'source',
        },
    )
    assert resp.status_code == 200
    html = resp.content.decode()
    assert 'This field is required' not in html
    assert 'The granter cannot be the user' in html

    resp = client.post(
        url,
        data={
            'user': user.id,
            'granter': granter.id,
            'is_staff': 'on',
            'source': 'bad',
        },
    )
    assert resp.status_code == 200
    html = resp.content.decode()
    assert 'This field is required' not in html
    assert 'bad source name' in html

    # Test a runtime error that doesnt happen as a result of normal
    # validation. It should be shown as a normal form error
    user.username = 'run_error'
    user.save()
    resp = client.post(
        url,
        data={
            'user': user.id,
            'granter': granter.id,
            'is_staff': False,
            'source': 'good',
        },
    )
    assert resp.status_code == 200
    assert 'Test runtime error' in resp.content.decode()

    # Test a valid post
    user.username = 'good'
    user.save()
    user.refresh_from_db()
    assert user.is_staff
    resp = client.post(
        url,
        data={
            'user': user.id,
            'granter': granter.id,
            'is_staff': False,
            'source': 'good',
        },
    )
    assert resp.status_code == 302
    user.refresh_from_db()
    assert not user.is_staff


@pytest.mark.django_db
def test_grant_staff_view_raise_run_errors(client):
    """Tests the grant staff view without showing run errors"""
    user = ddf.G(User, is_staff=True, username='run_error')
    granter = ddf.G(User, is_staff=True, is_superuser=True)
    url = urls.reverse('grant_staff_access_raise_run_errors')

    # Test a post that will result in a runtime error. Errors should
    # not be suppressed in this case
    with pytest.raises(RuntimeError):
        client.post(
            url,
            data={
                'user': user.id,
                'granter': granter.id,
                'is_staff': False,
                'source': 'good',
            },
        )


@pytest.mark.django_db
def test_grant_staff_object_view(client):
    user = ddf.G(User, is_staff=True)
    granter = ddf.G(User, is_staff=True, is_superuser=True)
    client.force_login(granter)

    # Test a 404
    url = urls.reverse('grant_staff_access_object', kwargs={'pk': 0})
    resp = client.get(url)
    assert resp.status_code == 404

    # Test a proper page load
    url = urls.reverse('grant_staff_access_object', kwargs={'pk': user.id})
    resp = client.get(url)
    assert resp.status_code == 200

    # Test a valid post
    assert user.is_staff
    resp = client.post(url, data={'is_staff': False, 'source': 'good'})
    assert resp.status_code == 302
    user.refresh_from_db()
    assert not user.is_staff


@pytest.mark.django_db
def test_grant_staff_objects_view(client):
    users = ddf.G(User, n=2, is_staff=True)
    granter = ddf.G(User, is_staff=True, is_superuser=True, username='GRANT')
    client.force_login(granter)

    # Test a 404 where no PKs are supplied
    url = urls.reverse('grant_staff_access_objects')
    resp = client.get(url)
    assert resp.status_code == 404

    # Test a 404 where no bad PKs are supplied
    url = urls.reverse('grant_staff_access_objects')
    url += f'?pk={users[0].id}&pk=0'
    resp = client.get(url)
    assert resp.status_code == 404

    # Test a proper page load
    url = urls.reverse('grant_staff_access_objects')
    url += f'?pk={users[0].id}&pk={users[1].id}'
    resp = client.get(url)
    assert resp.status_code == 200

    # Verify runtime errors don't result in success messages
    users[0].username = 'run_error'
    users[0].save()
    resp = client.post(url, data={'is_staff': False, 'source': 'good'})
    assert 'Test runtime error' in resp.content.decode()
    assert 'GRANT successfully' not in resp.content.decode()

    # Test a valid post
    users[0].username = 'good'
    users[0].save()
    for user in users:
        assert user.is_staff
    resp = client.post(url, data={'is_staff': False, 'source': 'good'})
    assert resp.status_code == 302
    for user in users:
        user.refresh_from_db()
        assert not user.is_staff

    # Verify that the valid post results in a success message
    resp = client.get(url)
    assert (
        'GRANT successfully granted staff access to users.'
        in resp.content.decode()
    )

    # Make both users have invalid usernames so we can check bulk errors
    users[0].username = 'bad_user1'
    users[0].save()
    users[1].username = 'bad_user2'
    users[1].save()
    resp = client.post(url, data={'is_staff': False, 'source': 'good'})
    assert resp.status_code == 200
    content = resp.content.decode()
    assert 'bad_user1: Bad username' in content
    assert 'bad_user2: Bad username' in content


@pytest.mark.django_db
def test_grant_staff_wizard_view(client):
    user = ddf.G(User, is_staff=True)
    granter = ddf.G(User, is_staff=True, is_superuser=True)
    url = urls.reverse('grant_staff_access_wizard')

    resp = client.get(url)
    html = resp.content.decode()
    # Verify the custom help text was rendered on our user field
    assert 'Help text' in html

    # Post no data. We should have a "field is required" errors
    resp = client.post(url, data={'grant_staff_wizard_view-current_step': '0'})
    assert resp.status_code == 200
    html = resp.content.decode()
    assert 'This field is required' in html

    # Post data and go to the next step
    resp = client.post(
        url,
        data={'grant_staff_wizard_view-current_step': '0', '0-user': user.id},
    )
    assert resp.status_code == 200
    html = resp.content.decode()
    assert 'Granter:' in html

    # Post the granter. Using the same user will result in a validation
    # error
    resp = client.post(
        url,
        data={
            'grant_staff_wizard_view-current_step': '1',
            '1-granter': user.id,
        },
    )
    assert resp.status_code == 200
    html = resp.content.decode()
    assert 'Granter must be superuser and staff' in html

    # Go to the next step
    resp = client.post(
        url,
        data={
            'grant_staff_wizard_view-current_step': '1',
            '1-granter': granter.id,
        },
    )
    assert resp.status_code == 200
    html = resp.content.decode()
    assert 'Is staff:' in html

    # Post a "False" staff flag. This edits the initial value for
    # the next step
    resp = client.post(
        url,
        data={
            'grant_staff_wizard_view-current_step': '2',
            '2-is_staff': False,
        },
    )
    assert resp.status_code == 200
    html = resp.content.decode()
    assert 'Source:' in html
    assert 'False' in html

    # Try to finish the wizard, but raise a runtime error.
    user.username = 'run_error'
    user.save()
    resp = client.post(
        url,
        data={
            'grant_staff_wizard_view-current_step': '3',
            '3-source': 'source',
        },
    )
    assert resp.status_code == 200
    assert 'Test runtime error' in resp.content.decode()

    # Finish the form wizard successfully
    user.username = 'good'
    user.save()
    resp = client.post(
        url,
        data={
            'grant_staff_wizard_view-current_step': '3',
            '3-source': 'source',
        },
    )
    assert resp.status_code == 302

    user.refresh_from_db()
    assert not user.is_staff


@pytest.mark.django_db
def test_grant_staff_wizard_view_raise_run_errors(client):
    user = ddf.G(User, is_staff=True, username='run_error')
    granter = ddf.G(User, is_staff=True, is_superuser=True)
    url = urls.reverse('grant_staff_access_wizard_raise_run_errors')

    # Post successful steps
    client.post(
        url,
        data={'grant_staff_wizard_view-current_step': '0', '0-user': user.id},
    )
    client.post(
        url,
        data={
            'grant_staff_wizard_view-current_step': '1',
            '1-granter': granter.id,
        },
    )
    client.post(
        url,
        data={
            'grant_staff_wizard_view-current_step': '2',
            '2-is_staff': False,
        },
    )

    # Finish the form wizard. A runtime error will be raised
    with pytest.raises(RuntimeError):
        client.post(
            url,
            data={
                'grant_staff_wizard_view-current_step': '3',
                '3-source': 'source',
            },
        )


@pytest.mark.django_db
def test_grant_staff_cond_wizard_view(client):
    user = ddf.G(User, is_staff=True)
    granter = ddf.G(User, is_staff=True, is_superuser=True)
    url = urls.reverse('grant_staff_access_cond_wizard')

    resp = client.get(url)
    html = resp.content.decode()
    # Verify the custom help text was rendered on our user field
    assert 'Help text' in html

    # Post no data. We should have a "field is required" errors
    resp = client.post(
        url, data={'grant_staff_cond_wizard_view-current_step': '0'}
    )
    assert resp.status_code == 200
    html = resp.content.decode()
    assert 'This field is required' in html

    # Post data and go to the next conditional step.
    # The conditional step is based on the value of "is_staff"
    resp = client.post(
        url,
        data={
            'grant_staff_cond_wizard_view-current_step': '0',
            '0-user': user.id,
            '0-granter': granter.id,
            '0-is_staff': True,
        },
    )
    assert resp.status_code == 200
    html = resp.content.decode()
    assert 'Staff is true!' in html

    # Try the other conditional step when the staff value is false
    resp = client.post(
        url,
        data={
            'grant_staff_cond_wizard_view-current_step': '0',
            '0-user': user.id,
            '0-granter': granter.id,
            '0-is_staff': False,
        },
    )
    assert resp.status_code == 200
    html = resp.content.decode()
    assert 'Staff is false!' in html

    # Post the granter. Using the same user will result in a validation
    # error
    resp = client.post(
        url,
        data={
            'grant_staff_cond_wizard_view-current_step': '2',
            '2-source': 'source',
        },
    )
    assert resp.status_code == 302

    user.refresh_from_db()
    assert not user.is_staff


@pytest.mark.django_db
def test_grant_staff_object_wizard_view(client):
    user = ddf.G(User, is_staff=True)
    granter = ddf.G(User, is_staff=True, is_superuser=True)
    url = urls.reverse(
        'grant_staff_access_object_wizard', kwargs={'pk': user.pk}
    )

    resp = client.get(url)
    html = resp.content.decode()
    assert 'Granter:' in html

    # Post the granter
    resp = client.post(
        url,
        data={
            'grant_staff_object_wizard_view-current_step': '0',
            '0-granter': granter.id,
        },
    )
    assert resp.status_code == 200
    html = resp.content.decode()
    assert 'Is staff:' in html

    # Post a "False" staff flag. This edits the initial value for
    # the next step
    resp = client.post(
        url,
        data={
            'grant_staff_object_wizard_view-current_step': '1',
            '1-is_staff': False,
        },
    )
    assert resp.status_code == 200
    html = resp.content.decode()
    assert 'Source:' in html
    assert 'False' in html

    # Verify we can render runtime errors and ignore success messages
    user.username = 'run_error'
    user.save()
    resp = client.post(
        url,
        data={
            'grant_staff_object_wizard_view-current_step': '2',
            '2-source': 'source',
        },
    )
    assert 'Test runtime error' in resp.content.decode()
    assert f'Successfully granted' not in resp.content.decode()

    # Finish the form wizard
    user.username = 'good'
    user.save()
    resp = client.post(
        url,
        data={
            'grant_staff_object_wizard_view-current_step': '2',
            '2-source': 'source',
        },
    )
    assert resp.status_code == 302

    user.refresh_from_db()
    assert not user.is_staff

    # Verify the proper success message is rendered
    resp = client.get(url)
    assert resp.status_code == 200
    assert f'Successfully granted access to {user}.' in resp.content.decode()
