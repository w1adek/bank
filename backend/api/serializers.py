import re

from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from . import models

class CustmerRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Customer
        fields = ['id', 'name', 'surname', 'email', 'phone', 'address', 'secret_answer', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def validate_name(self, value):
        if not value.isalpha():
            raise serializers.ValidationError('name must only contain letters.')
        value = value.capitalize()
        return value
    
    def validate_surname(self, value):
        if not value.isalpha():
            raise serializers.ValidationError('surname must only contain letters.')
        value = value.capitalize()
        return value
    
    def validate_email(self, value):
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError('invalid email address.')
        return value
    
    def validate_phone(self, value):
        phone_regex = r'(?<!\w)(\(?(\+|00)?48\)?)?[ -]?\d{3}[ -]?\d{3}[ -]?\d{3}(?!\w)'
        if not re.match(phone_regex, value):
            raise serializers.ValidationError("invalid phone number format.")
        value = re.sub(r'\D', '', value)
        return value
    
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError('password must be at least 8 characters long.')
        return value
    
    def create(self, validated_data):
        name = validated_data['name']
        surname = validated_data['surname']
        email = validated_data['email']
        phone = validated_data['phone']
        address = validated_data['address']
        secret_answer = validated_data['secret_answer']
        password = make_password(validated_data['password'])
        
        customer = models.Customer.objects.create(
            name=name,
            surname=surname,
            email=email,
            phone=phone,
            address=address,
            secret_answer=secret_answer,
            password=password
        )
        customer.save()
        return customer
    

class CustomerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Customer
        fields = ['email', 'phone', 'address']

    def validate_email(self, value):
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError('invalid email address.')
        return value

    def validate_phone(self, value):
        phone_regex = r'(?<!\w)(\(?(\+|00)?48\)?)?[ -]?\d{3}[ -]?\d{3}[ -]?\d{3}(?!\w)'
        if not re.match(phone_regex, value):
            raise serializers.ValidationError("invalid phone number format.")
        value = re.sub(r'\D', '', value)
        return value

    def update(self, customer, validated_data):
        customer.email = validated_data.get('email', customer.email)
        customer.phone = validated_data.get('phone', customer.phone)
        customer.address = validated_data.get('address', customer.address)
        customer.save()
        return customer


class AccountOpenSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Account
        fields = ['type']

    def create(self, validated_data):
        customer_id = validated_data['customer_id']
        type = validated_data['type']
        balance = 0
                
        account = models.Account.objects.create(
            customer_id=customer_id,
            type=type,
            balance=0
        )
        account.save()
        return account
    
    
class UpdatePasswordSerializer(serializers.Serializer):
    secret_answer = serializers.CharField(max_length=50)
    new_password = serializers.CharField(write_only=True)

    def validate_secret_answer(self, value):
        customer = self.context['request'].user
        if customer.secret_answer != value:
            raise serializers.ValidationError("incorrect secret answer.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError('password must be at least 8 characters long.')
        return value

    def update_password(self, customer, validated_data):
        new_password = validated_data['new_password']
        hashed_password = make_password(new_password)
        customer.password = hashed_password
        customer.save()
        return customer
    
    
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Transaction
        fields = ['account', 'recipient', 'type', 'amount', 'date', 'time', 'status']