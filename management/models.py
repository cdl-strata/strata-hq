from django.db import models
from django.core.validators import validate_slug

# Sites - A data center. Examples: hdc, sdc
class Site(models.Model):
    """Model for sites aka data centers"""
    name = models.CharField(max_length=32, unique=True, validators=[validate_slug],
                            help_text='The common short name of the site. For example: "hdc", "sdc" or "ldn"')
    description = models.CharField(max_length=32, blank=True,
                                   help_text='Examples: "Hindley Street", "Strata House" or "Andy\'s desk"')
    notes = models.TextField(max_length=1024, blank=True)

    def __str__(self):
         return '%s - %s' % (self.name, self.description)

# Teams - Who has ownership of the asset - Examples: "Web Services", "Strata Engineering" or "Windows Team"
class Team(models.Model):
    """Model for teams or asset owners"""
    name = models.CharField(max_length=32, unique=True,
                            help_text='Team name. Examples: "Strata Admin", "Network Team" or "Citrix Admin"')
    email = models.EmailField()
    notes = models.TextField(max_length=1024, blank=True)

    def __str__(self):
        return self.name