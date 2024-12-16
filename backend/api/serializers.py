import re

from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from . import models

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Branch
        fields = ['address', 'open_time', 'close_time']

class CustomerRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Customer
        fields = ['id', 'name', 'surname', 'email', 'phone', 'address', 'secret_answer', 'password_hash']
    
    def validate_name(self, value):
        if not value.isalpha():
            raise serializers.ValidationError("Name can only contain letters")
        
        value = value.capitalize()
        return value

    def validate_surname(self, value):
        if not value.isalpha():
            raise serializers.ValidationError("Surname can only contain letters")
        
        value = value.capitalize()
        return value
    
    def validate_email(self, value):
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Invalid email format")
        return value
    
    def validate_phone(self, value):
        phone_regex = r'(?<!\w)(\(?(\+|00)?48\)?)?[ -]?\d{3}[ -]?\d{3}[ -]?\d{3}(?!\w)'
        if not re.match(phone_regex, value):
            raise serializers.ValidationError("Invalid phone number format")
        
        value = re.sub(r'\D', '', value)
        return value
    
    def validate_password_hash(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
    
    def create(self, validated_data):
        hashed_password = make_password(validated_data['password_hash'])
        validated_data['password_hash'] = hashed_password
        
        customer = models.Customer.objects.create(**validated_data)
        return customer
    

class AccountOpenSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Account
        fields = ['id', 'customer', 'type', 'balance']
        read_only_fields = ['balance']

    def create(self, validated_data):
        account = models.Account.objects.create(
            customer=validated_data['customer'],
            type=validated_data['type'],
            balance=0
        )
        return account
    

