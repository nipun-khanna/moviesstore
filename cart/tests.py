from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from movies.models import Movie
from .models import Item, Order


class AdminPageTests(TestCase):
    def setUp(self):
        self.staff = get_user_model().objects.create_user(
            username='staff', is_staff=True, is_superuser=True
        )
        self.client.force_login(self.staff)

    def test_admin_pages_render_with_top_buyer_link(self):
        for url in (reverse('admin:index'), reverse('admin:cart_order_changelist')):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, reverse('top_buyer'))

    def test_top_buyer_with_no_purchases(self):
        response = self.client.get(reverse('top_buyer'))
        self.assertContains(response, 'no movies purchased yet')
        self.assertIsNone(response.context['buyer'])

    def test_top_buyer_counts_quantities_across_orders(self):
        buyer = get_user_model().objects.create_user(username='buyer')
        movie = Movie.objects.create(name='Movie', price=10)
        for user, quantity in ((self.staff, 3), (buyer, 2), (buyer, 2)):
            order = Order.objects.create(user=user, total=10 * quantity)
            Item.objects.create(order=order, movie=movie, price=10, quantity=quantity)
        response = self.client.get(reverse('top_buyer'))
        self.assertContains(response, 'User: buyer')
        self.assertEqual(response.context['buyer'].movies_purchased, 4)

    def test_top_buyer_requires_staff(self):
        self.client.logout()
        response = self.client.get(reverse('top_buyer'))
        self.assertRedirects(
            response, reverse('admin:login') + '?next=' + reverse('top_buyer')
        )
        user = get_user_model().objects.create_user(username='customer')
        self.client.force_login(user)
        response = self.client.get(reverse('top_buyer'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('admin:login')))
