from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

class Client(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    tax = models.FloatField(max_length=10, default= 0.0)
    created_by = models.CharField(max_length=100, blank=True, null=True)
    #street_address = models.CharField(max_length=255)
    #city = models.CharField(max_length=100)
    #state = models.CharField(max_length=50)
    #postal_code = models.CharField(max_length=20)
    tax = models.FloatField(default=0.0)

    def __str__(self):
        return self.name
    
class ClientContact(models.Model):
    STATUS_CHOICES = [
        ('Primary', 'primary'),
        ('WorkOrder', 'WorkOrder'),
        ('Normal', 'Normal')
    ]
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, null=True)  # Changed to CharField
    email = models.EmailField()
    client = models.ForeignKey(Client, on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Normal')
    created_by = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class ProductType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Color(models.Model):
    color = models.CharField(max_length=50)

    def __str__(self):
        return self.color

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE)
    created_by = models.CharField(max_length=100, blank=True, null=True)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, blank=True, null=True) # i need to get rid of this?

    def __str__(self):
        return self.name
    

    
class Discount(models.Model):
    amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.amount)
    
class Tax(models.Model):
    amount = models.FloatField()
    description = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.amount)
    

class Invoice(models.Model):
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Sent', 'Sent'),
        ('Paid', 'Paid'),
        ('Overdue', 'Overdue'),
    ]

    # Auto-incrementing primary key
    invoice_num = models.AutoField(primary_key=True)

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    invoice_date = models.DateField()
    items = models.ManyToManyField(Product, through='InvoiceItem', blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Draft')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return str(self.invoice_num)

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    number = models.CharField(max_length=10, default="")
    created_by = models.CharField(max_length=100, blank=True, null=True)


class WorkOrders(models.Model):
    STATUS_CHOICES = [
        ('Waiting_on_Assignment', 'Waiting on Assignment'),
        ('Being_Worked_On', 'Being Worked On'),
        ('Ready', 'Ready'),
        ('Delivered', 'Delivered'),
        ('Rush', 'Rush'),
    ]

    # Auto-incrementing primary key
    workOrder_num = models.AutoField(primary_key=True)

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    workOrder_date = models.DateField()
    items = models.ManyToManyField(Product, through='WorkorderItem', blank=True)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default="Waiting_on_Assignment")
    created_at = models.DateTimeField(auto_now_add=True)
    is_rush = models.BooleanField(default=False)
    return_by = models.DateField(null=True, default=None)
    quote_required = models.BooleanField(default=False)
    specialInstructions = models.CharField(max_length=250, default="", null=True, blank=True)
    created_by = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=100, blank=True, null=True)
    account_contact = models.ForeignKey(ClientContact, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.workOrder_num)
    

class WorkOrderItem(models.Model):
    STATUS_CHOICES = [
        ('Waiting_on_Assignment', 'Waiting on Assignment'),
        ('Checked_Out', 'Checked Out'),
        ('Needs_QC', 'Needs QC'),
        ('Parts_On_Order', 'Parts On Order'),
        ('QC_PASS', 'QC PASS'),
        ('QC_FAIL', 'QC FAIL'),
    ]

    QC_STATUS_CHOICES = [
        ('QC_FAIL', 'QC FAIL'),
        ('QC_PASS', 'QC PASS'),
        ('WAITING_QC', 'Waiting On QC'),
        ('NO_QC', '')
    ]



    workOrder = models.ForeignKey(WorkOrders, on_delete=models.CASCADE)
    
    # Set product to allow blank and null values
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100, blank=True, null=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField(max_length=35, blank=True, null=True)
    issue = models.TextField(max_length=125, blank=True, null=True)
    mfgnum = models.CharField(max_length=50, blank=True, null=True)
    number = models.CharField(max_length=10, default="", blank=True, null=True)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default="Waiting_on_Assignment")
    qc = models.CharField(max_length=20, choices=QC_STATUS_CHOICES, default="NO_QC")
    color = models.ForeignKey(Color, on_delete=models.CASCADE, blank=True, null=True)
    
    # Add fields for custom product
    custom_product_name = models.CharField(max_length=200, blank=True, null=True)
    custom_product_description = models.TextField(max_length=100, blank=True, null=True)
    custom_product_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    technician = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)


    def save(self, *args, **kwargs):
        self.last_updated_at = timezone.now()
        super(WorkOrderItem, self).save(*args, **kwargs)

class Signature(models.Model):
    image = models.ImageField(upload_to='static/img/signatures/') # make non editable
    customer_last_name = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    workOrder = models.ForeignKey(WorkOrders, on_delete=models.CASCADE) # remove default

    def __str__(self):
        return f'Signature {self.id}'
    
class CompanyRepSignature(models.Model):
    companyRep = models.ImageField(upload_to='static/img/signatures/') # make non editable
    last_name = models.CharField(max_length=50, blank=True, null=True)
    workOrder = models.ForeignKey(WorkOrders, on_delete=models.CASCADE) # remove default
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Signature {self.id}'
    

        

