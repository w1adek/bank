from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.views import APIView
from . import models
from . import serializers


# Create your views here.
class BranchList(generics.ListAPIView):
    queryset = models.Branch.objects.all()
    serializer_class = serializers.BranchSerializer


class CustomerRegistrationView(generics.GenericAPIView):
    serializer_class = serializers.CustomerRegistrationSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Customer registered successfully'}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class AccountOpenView(generics.GenericAPIView):
    serializer_class = serializers.AccountOpenSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Account opened successfully'}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)