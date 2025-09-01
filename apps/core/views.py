import random
import logging
import os
import requests

from django.shortcuts import render

from rest_framework import viewsets

logger = logging.getLogger('django')

def generate_otp():
    otp = str(random.randint(100000, 999999))
    logger.info(f"Generated OTP: {otp}")
    return otp

def send_otp_sms(phone, otp):
    url = "https://samayasms.com.np/smsapi/index.php"
    payload = {
        'key': os.environ.get('SMS_API_KEY'),
        'routeid': os.environ.get('SMS_ROUTE_ID'),
        'type': 'text',
        'contacts': phone,
        'senderid': os.environ.get('SMS_SENDER_ID'),
        'msg': f'Your OTP is {otp}'
    }
    try:
        response = requests.post(url, data=payload)
        logger.info(f"SMS sent to {phone}, API status: {response.status_code}, response: {response.text}")
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to send SMS to {phone}: {e}")

class MunicipalityTenantModelViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        # Assumes model has a ForeignKey to Municipality named 'municipality'
        base_queryset = super().get_queryset()
        return base_queryset.filter(municipality=self.request.tenant)

    def perform_create(self, serializer, **kwargs):
        # Automatically attach municipality from the request
        serializer.save(municipality=self.request.tenant, **kwargs)
