from django.db import models


# Customers
class Customer(models.Model):
    name = models.CharField(max_length=1024)

    def __str__(self):
        return self.name

# Servers
class Server(models.Model):
    hostname = models.CharField(max_length=1024, unique=True)
    adminserver_port = models.IntegerField(default=1700)
    adminserver_username = models.CharField(max_length=64, default="weblogic")
    adminserver_password = models.CharField(max_length=64, default="weblogic")
    customer = models.ManyToManyField(Customer)

    ENVIRONMENTS = (
        ('dev', 'Development'),
        ('test', 'Test'),
        ('uat', 'UAT'),
        ('live', 'Live'),
    )
    environment = models.CharField(max_length=10, choices=ENVIRONMENTS, default="dev")

    def __str__(self):
        return self.hostname