import requests
import base64
from datetime import datetime
from django.conf import settings


def get_access_token():
    """
    Get Safaricom OAuth access token
    """

    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET

    api_url = (
        "https://sandbox.safaricom.co.ke/oauth/v1/generate"
        "?grant_type=client_credentials"
    )

    response = requests.get(
        api_url,
        auth=(consumer_key, consumer_secret)
    )

    return response.json().get("access_token")


def stk_push(
    phone_number,
    amount,
    account_reference,
    transaction_desc
):
    """
    Send STK Push request
    """

    access_token = get_access_token()

    url = (
        "https://sandbox.safaricom.co.ke/"
        "mpesa/stkpush/v1/processrequest"
    )

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    shortcode = settings.MPESA_SHORTCODE
    passkey = settings.MPESA_PASSKEY

    password = base64.b64encode(
        (
            shortcode +
            passkey +
            timestamp
        ).encode()
    ).decode()

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone_number,
        "PartyB": shortcode,
        "PhoneNumber": phone_number,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc,
    }

    response = requests.post(
        url,
        json=payload,
        headers=headers
    )

    return response.json()