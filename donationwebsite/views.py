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