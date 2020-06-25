import arg
from django.db import models


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

    def __init__(self, objects, *, qset=None, model=None, pk='pk'):
        super().__init__()
        assert isinstance(objects, str)
        if model is None and qset is None:
            raise ValueError('Must provide model or qset to djarg.qset')

        self._qset = qset if qset is not None else model._default_manager.all()
        self._objects = arg.val(objects)
        self._pk = pk

    def _call(self, **call_args):
        objects = arg.load(self._objects, **call_args)

        if isinstance(objects, models.QuerySet):
            return objects

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
            return self._qset.filter(
                **{pk_in: [getattr(obj, self._pk) for obj in objects]}
            )
        else:
            return self._qset.filter(**{pk_in: objects})
