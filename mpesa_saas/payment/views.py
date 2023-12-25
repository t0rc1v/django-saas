from django.shortcuts import render, redirect, reverse, get_object_or_404
# from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse


import requests
import json
import base64
from datetime import datetime
import os
from dotenv import load_dotenv

from .models import CheckoutId
from course.models import Course

# Load the stored environment variables
load_dotenv()

#env variables
CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
PHONE = os.getenv("PHONE")
PASSKEY = os.getenv("PASSKEY")
BUSINESS_SHORT_CODE = os.getenv("BUSINESS_SHORT_CODE")


def get_access_token():
    consumer_key = CONSUMER_KEY  # Fill with your app Consumer Key
    consumer_secret = CONSUMER_SECRET  # Fill with your app Consumer Secret
    access_token_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    headers = {'Content-Type': 'application/json'}
    auth = (consumer_key, consumer_secret)
    try:
        response = requests.get(access_token_url, headers=headers, auth=auth)
        response.raise_for_status()  # Raise exception for non-2xx status codes
        result = response.json()
        access_token = result['access_token']
        return JsonResponse({'access_token': access_token})
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)})

@login_required    
def create_checkout_session(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    access_token_response = get_access_token()
    if isinstance(access_token_response, JsonResponse):
        access_token = access_token_response.content.decode('utf-8')
        access_token_json = json.loads(access_token)
        access_token = access_token_json.get('access_token')
        if access_token:
            amount = course.price
            phone = PHONE
            process_request_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
            callback_url = 'https://eea5-102-219-210-185.ngrok-free.app/course_sucess'
            passkey = PASSKEY
            business_short_code = BUSINESS_SHORT_CODE
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()
            party_a = phone
            # party_b = '254708374149'
            account_reference = 'push test'
            transaction_desc = 'stkpush test'
            stk_push_headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + access_token
            }
            
            stk_push_payload = {
                'BusinessShortCode': business_short_code,
                'Password': password,
                'Timestamp': timestamp,
                'TransactionType': 'CustomerPayBillOnline',
                'Amount': amount,
                'PartyA': party_a,
                'PartyB': business_short_code,
                'PhoneNumber': party_a,
                'CallBackURL': callback_url,
                'AccountReference': account_reference,
                'TransactionDesc': transaction_desc
            }

            try:
                response = requests.post(process_request_url, headers=stk_push_headers, json=stk_push_payload)
                response.raise_for_status()   
                # Raise exception for non-2xx status codes
                response_data = response.json()
                response_code = response_data['ResponseCode']

                # if stk_push successful save the following
                if response_code == "0":
                    event = CheckoutId(payer=request.user, checkout_id=response_data['CheckoutRequestID'], course_id=course.id)
                    event.save()
                
                return render(request, "payment/processing.html")

            except requests.exceptions.RequestException as e:
                return JsonResponse({'error': str(e)})
        else:
            return JsonResponse({'error': 'Access token not found.'})
    else:
        return JsonResponse({'error': 'Failed to retrieve access token.'})

@login_required
def handle_checkout_session(request):
    checkout = CheckoutId.objects.filter(payer=request.user)

    # checkout object for the latest transaction
    last = checkout.last()

    access_token_response = get_access_token()
    if isinstance(access_token_response, JsonResponse):
        access_token = access_token_response.content.decode('utf-8')
        access_token_json = json.loads(access_token)
        access_token = access_token_json.get('access_token')
        if access_token:
            query_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query'
            business_short_code = BUSINESS_SHORT_CODE
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            passkey = PASSKEY
            password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()

            query_headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + access_token
            }

            query_payload = {
                'BusinessShortCode': business_short_code,
                'Password': password,
                'Timestamp': timestamp,
                'CheckoutRequestID': last.checkout_id
            }
            
            try:
                response = requests.post(query_url, headers=query_headers, json=query_payload)
                response = response.json()

                # response.raise_for_status()
                # Raise exception for non-2xx status codes

                response_code = response.get("ResponseCode")
                result_code = response.get("ResultCode")
                # result_code = response_data['ResultCode']

                # EXPECTED RESULT CODES 
                '''
                0 - The transaction was successful
                1 - The balance is insufficient for the transaction
                1032 - Transaction has been canceled by the user
                1037 - Timeout in completing transaction
                '''

                if result_code == '0':
                    user = request.user

                    course = get_object_or_404(Course, pk=last.course_id)
                    course.subscribers.add(user)
                else:
                    pass

                return redirect("course_success")

            except requests.exceptions.RequestException as e:
                return JsonResponse({'error': 'Error: ' + str(e)})  # Return JSON response for network error
            except json.JSONDecodeError as e:
                return JsonResponse({'error': 'Error decoding JSON: ' + str(e)})  # Return JSON response for JSON decoding error
        else:
            return JsonResponse({'error': 'Access token not found.'})
    else:
        return JsonResponse({'error': 'Failed to retrieve access token.'})

@login_required
def course_success(request):
    return redirect("course_list")

@login_required
def course_cancel(request):
    return redirect("course_list")

