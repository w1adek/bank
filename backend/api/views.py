from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics
from .models import *
from .serializers import *


# Create your views here.
class CustomerRegistrationView(generics.GenericAPIView):
    serializer_class = CustomerRegistrationSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            customer = serializer.save()
            
            return Response({
                'message': 'Customer registered successfully',
                'customer_id': customer.id,
                'name': customer.name,
                'surname': customer.surname,
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)