import arg
from django.db import models


def _attach_select_for_update(qset, select_for_update):
    """
    Given a queryset, attach select_for_update parameters if we
    are not runnnig in a partial python-args call (i.e. don't lock
    the queryset if we are only running validators).

    select_for_update can be one of:
    1. dict: Calls select_for_update with kwargs
    2. List[str]: Calls select_for_update with this passed to the "of"
       argument
    3. None: No select_for_update is ever applied.
    4. True: select_for_update is applied with default arguments

    If we are running in a partial python-args mode, no select_for_update
    will be applied.
    """
    if (
        arg.call()
        and not arg.call().is_partial
        and select_for_update is not None
    ):
        if isinstance(select_for_update, dict):
            return qset.select_for_update(**select_for_update)
        elif isinstance(select_for_update, (list, tuple)):
            return qset.select_for_update(of=select_for_update)
        else:
            return qset.select_for_update()
    else:
        return qset


class qset(arg.Lazy):
    """
    Lazily coerces a value into a queryset. Can be used inside
    of ``python-args`` decorators.

    Can coerce the following types:

    1. ``Queryset``: Returns the queryset.
    2. ``None``: Returns an empty queryset.
    3. ``<primary key>``: Returns queryset with single element.
    4. ``Model``: Returns queryset with single model.
    5. ``List[<primary key>]``: Returns queryset with all elements.
    6. ``List[Model]``: Returns queryset with all models.

    Args:
        objects (str): The argument name to be evaluated.
        qset (QuerySet): The queryset to use for the initial queryset when a
            list of values is provided.
        model (Model): The model to use for the queryset when a list of
            values is provided.
        select_for_update (List[str], default=None): Adds a select_for_update
            using the provided arguments. Does *not* perform select_for_update
            when running in partial mode. If a list is provided,
            the list is used as the ``of`` argument for ``select_for_update``.
            If a dictionary is provided, the values are passed as kwargs
            to ``select_for_update``. If ``True`` is provided, no arguments
            are passed to ``select_for_update``.

    Examples:
        Using `djarg.qset` with ``python-args`` ``arg.default`` decorator::

            import arg
            import djarg

            @arg.defaults(
                profiles=djarg.qset('profiles', model=Profile).select_related('address')
            )
            def fetch_zip_codes(profiles):
                return [profile.address.zip for profile in profiles]

            # All of these invocations can be used
            fetch_zip_codes(Profile.objects.all())
            # A single model object
            fetch_zip_codes(single_profile_object)
            # A single PK
            fetch_zip_codes(1)
            # Lists of PKs or model objects
            fetch_zip_codes([2, 3])
            fetch_zip_codes([Profile(...), Profile(...)])
    """

    def __init__(
        self,
        objects,
        *,
        qset=None,
        model=None,
        pk='pk',
        select_for_update=None,
    ):
        super().__init__()
        assert isinstance(objects, str)
        if model is None and qset is None:
            raise ValueError('Must provide model or qset to djarg.qset')

        self._qset = qset if qset is not None else model._default_manager.all()
        self._objects = arg.val(objects)
        self._pk = pk
        self._select_for_update = select_for_update

    def _attach_select_for_update(self, qset):
        return _attach_select_for_update(qset, self._select_for_update)

    def _call(self, **call_args):
        objects = arg.load(self._objects, **call_args)

        if isinstance(objects, models.QuerySet):
            return self._attach_select_for_update(objects)

        # No object. Return empty queryset
        if objects is None:
            return self._qset.none()

        # Ensure we are always working with a list from now on
        if not isinstance(objects, (list, tuple)):
            objects = [objects]

        # Empty list. Return empty queryset
        if not objects:
            return self._qset.none()

        # Handle list of models or list of pks
        pk_in = f'{self._pk}__in'
        if isinstance(objects[0], models.Model):
            return self._attach_select_for_update(
                self._qset.filter(
                    **{pk_in: [getattr(obj, self._pk) for obj in objects]}
                )
            )
        else:
            return self._attach_select_for_update(
                self._qset.filter(**{pk_in: objects})
            )
