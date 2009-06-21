from django_evolution.mutations import ChangeField
from django.db import models


MUTATIONS = [
    ChangeField('Release', 'release_num', initial=None, null=True)
]
