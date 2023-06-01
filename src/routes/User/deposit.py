import stripe
from flask import Blueprint, jsonify, request
from __init__ import token_required

@token_required
def payment_sheet():
    
# Set your secret key. Remember to switch to your live secret key in production.
# See your keys here: https://dashboard.stripe.com/apikeys
    stripe.api_key = 'sk_test_51JZbuNCVJQzDKTXl0pfFYofioX0EMln8SGt6Pp0OJDIzQSbzb85gZHs6XOK043bXmOlnCZ9cRM1MzbeoPdaxNOfn000UYik44P'
  # Use an existing Customer ID if this is a returning customer
    customer = stripe.Customer.create()
    ephemeralKey = stripe.EphemeralKey.create(
        customer=customer['id'],
        stripe_version='2022-11-15',
    )
    paymentIntent = stripe.PaymentIntent.create(
        amount=1099,
        currency='eur',
        customer=customer['id'],
        automatic_payment_methods={
        'enabled': True,
        },
    )
    return jsonify(paymentIntent=paymentIntent.client_secret,
                    ephemeralKey=ephemeralKey.secret,
                    customer=customer.id,
                    publishableKey='pk_test_wk6O7Cc5k3McBIG2Hut2irGs')
