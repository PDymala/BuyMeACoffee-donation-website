from django.core.mail import send_mail
from django.shortcuts import redirect
from django.views import View
import stripe
from django.conf import settings
from django.views.generic import TemplateView

stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        price = Price.objects.get(id=self.kwargs["pk"])
        domain = "https://yourdomain.com"
        if settings.DEBUG:
            domain = "http://127.0.0.1:8000"
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price': price.stripe_price_id,
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=domain + '/success/',
            cancel_url=domain + '/cancel/',
        )
        return redirect(checkout_session.url)


class SuccessView(TemplateView):
    template_name = "success.html"


class CancelView(TemplateView):
    template_name = "cancel.html"

from .models import Product, Price


class ProductLandingPageView(TemplateView):
    template_name = "landing.html"
    # one products with multiple prices
    # def get_context_data(self, **kwargs):
    #     product = Product.objects.get(name="Sunglasses")
    #     prices = Price.objects.filter(product=product)
    #     context = super(ProductLandingPageView,
    #                     self).get_context_data(**kwargs)
    #     context.update({
    #         "product": product,
    #         "prices": prices
    #     })
    #     return context

    # multiple products with 1 price
    def get_context_data(self, **kwargs):
        products_in_db = Product.objects.all()

        products_with_prices = {}
        for product in products_in_db:
            products_with_prices[product] = Price.objects.filter(product=product)[0]

        context = super(ProductLandingPageView,
                        self).get_context_data(**kwargs)
        context.update({
            "products": products_with_prices
        })



        return context


from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_email = session["customer_details"]["email"]
        payment_intent = session["payment_intent"]

        # Handle the checkout.session.completed event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            customer_email = session["customer_details"]["email"]
            line_items = stripe.checkout.Session.list_line_items(session["id"])

            stripe_price_id = line_items["data"][0]["price"]["id"]
            price = Price.objects.get(stripe_price_id=stripe_price_id)
            product = price.product

            send_mail(
                subject="Here is your product",
                message=f"Thanks for your donation.",
                recipient_list=[customer_email],
                from_email="your@email.com"
            )

    return HttpResponse(status=200)