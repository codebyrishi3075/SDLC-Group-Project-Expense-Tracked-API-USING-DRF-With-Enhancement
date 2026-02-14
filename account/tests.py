from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch

from account.models import User, EmailOTP
from api_budgets.models import BudgetCategory, Budget
from api_expenses.models import Expense

# Integration tests for all API endpoints
class APITestSuite(APITestCase):
    def setUp(self):
        # ensure emails go to memory
        settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

        # create a verified user for authenticated endpoints
        self.user = User.objects.create_user(
            email='user@example.com',
            username='user',
            password='pass1234',
            is_email_verified=True,
            is_active=True
        )
        self.client = APIClient()
        # login the user to obtain token
        login_res = self.client.post(
            '/api/account/login/',
            {'email': 'user@example.com', 'password': 'pass1234'},
            format='json'
        )
        assert login_res.status_code == 200, 'setup login failed'
        self.token = login_res.data.get('access')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_account_registration_and_auth_flows(self):
        # register a new user while patching OTP generator to a known value
        with patch('account.views.generate_otp', return_value='654321'):
            res = self.client.post(
                '/api/account/register/',
                {
                    'email': 'new@example.com',
                    'username': 'newuser',
                    'password': 'newpass',
                    'confirm_password': 'newpass',
                    'full_name': 'New User'
                },
                format='json'
            )
            if res.status_code != 201:
                print('registration response:', res.status_code, res.data)
            self.assertEqual(res.status_code, 201)
            # OTP should have been created
            user = User.objects.get(email='new@example.com')
            otp_obj = EmailOTP.objects.filter(user=user).last()
            self.assertIsNotNone(otp_obj)
            self.assertEqual(otp_obj.otp, '654321')
            # verify the OTP
            verify_res = self.client.post(
                '/api/account/verify-otp/',
                {'email': 'new@example.com', 'otp': '654321'},
                format='json'
            )
            self.assertEqual(verify_res.status_code, 200)
            # login with new user
            login_res = self.client.post(
                '/api/account/login/',
                {'email': 'new@example.com', 'password': 'newpass'},
                format='json'
            )
            self.assertEqual(login_res.status_code, 200)

    def test_profile_and_password_endpoints(self):
        # fetch profile
        prof = self.client.get('/api/account/profile/')
        self.assertEqual(prof.status_code, 200)
        # update profile
        upd = self.client.put(
            '/api/account/profile/update/',
            {'first_name': 'Updated', 'last_name': 'Name'},
            format='json'
        )
        self.assertEqual(upd.status_code, 200)
        # upload avatar (simple text file)
        file_obj = SimpleUploadedFile('avatar.png', b'testimage', content_type='image/png')
        upav = self.client.post('/api/account/profile/avatar/', {'profile_image': file_obj}, format='multipart')
        self.assertEqual(upav.status_code, 200)

        # password reset request -> verify -> confirm
        # create an unverified user for password flow (mark verified so that login works after)
        pwd_user = User.objects.create_user(email='pwd@example.com', username='pwd', password='oldpass', is_email_verified=True)
        with patch('account.views.generate_otp', return_value='111111'):
            req = self.client.post('/api/account/password-reset/request/', {'email': 'pwd@example.com'}, format='json')
            self.assertEqual(req.status_code, 200)
            otp_obj = EmailOTP.objects.filter(user=pwd_user, purpose='reset').last()
            self.assertIsNotNone(otp_obj)
            self.assertEqual(otp_obj.otp, '111111')
            ver = self.client.post('/api/account/password-reset/verify-otp/', {'email': 'pwd@example.com', 'otp': '111111'}, format='json')
            self.assertEqual(ver.status_code, 200)
            conf = self.client.post('/api/account/password-reset/confirm/', {'email': 'pwd@example.com', 'new_password': 'newpass123'}, format='json')
            self.assertEqual(conf.status_code, 200)
            # confirm login works with new password
            login_res = self.client.post('/api/account/login/', {'email': 'pwd@example.com', 'password': 'newpass123'}, format='json')
            if login_res.status_code != 200:
                print('post-reset login', login_res.status_code, login_res.data)
            self.assertEqual(login_res.status_code, 200)

    def test_user_settings_endpoints(self):
        # GET default settings (should succeed)
        r = self.client.get('/api/usersettings/')
        self.assertIn(r.status_code, (200, 404))  # may be empty
        # update settings - change currency
        r2 = self.client.put('/api/usersettings/update/', {'currency': 'USD'}, format='json')
        self.assertIn(r2.status_code, (200, 201))
        # verify currency was updated
        r3 = self.client.get('/api/usersettings/')
        self.assertEqual(r3.status_code, 200)
        self.assertEqual(r3.data.get('data', {}).get('currency'), 'USD')
        
    def test_currency_options_endpoint(self):
        # Test currency options - public endpoint, no auth required
        from rest_framework.test import APIClient as AnonClient
        anon = AnonClient()
        r = anon.get('/api/usersettings/currencies/')
        self.assertEqual(r.status_code, 200)
        self.assertIn('data', r.data)
        currencies = r.data['data']
        # Should have at least USD, EUR, INR
        codes = [c['code'] for c in currencies]
        self.assertIn('USD', codes)
        self.assertIn('EUR', codes)
        self.assertIn('INR', codes)

    def test_budget_and_expense_endpoints(self):
        # create a category
        cat_res = self.client.post('/api/budgets/create/', {'name': 'Food'}, format='json')
        self.assertEqual(cat_res.status_code, 201)
        cat_id = cat_res.data['data']['id']
        # make sure id exists
        self.assertIsNotNone(cat_id)
        # list categories
        lc = self.client.get('/api/budgets/')
        self.assertEqual(lc.status_code, 200)
        # update category
        upd = self.client.put(f'/api/budgets/update/{cat_id}/', {'name': 'Groceries'}, format='json')
        self.assertEqual(upd.status_code, 200)
        # create a budget
        # month must be in YYYY-MM-DD format
        bud_res = self.client.post('/api/budgets/budgets/create/', {'category': cat_id, 'amount': '500.00', 'month': '2026-02-01'}, format='json')
        if bud_res.status_code != 201:
            print('budget create error', bud_res.status_code, bud_res.data)
        self.assertEqual(bud_res.status_code, 201)
        bud_id = bud_res.data['data']['id']
        # list budgets
        lb = self.client.get('/api/budgets/budgets/')
        self.assertEqual(lb.status_code, 200)
        # utilization (should work even if no expenses)
        util = self.client.get('/api/budgets/budgets/utilization/?month=2026-02')
        self.assertEqual(util.status_code, 200)
        # update budget
        upd_bud = self.client.put(f'/api/budgets/budgets/{bud_id}/update/', {'amount':'600.00'}, format='json')
        self.assertEqual(upd_bud.status_code, 200)
        # expenses: create one
        exp_res = self.client.post('/api/expenses/create/', {'category': cat_id, 'amount': '45.50', 'date': '2026-02-14', 'description': 'Test'}, format='json')
        if exp_res.status_code != 201:
            print('expense create response', exp_res.status_code, exp_res.data)
        self.assertEqual(exp_res.status_code, 201)
        exp_id = exp_res.data['data']['id']
        # list expenses
        le = self.client.get('/api/expenses/')
        self.assertEqual(le.status_code, 200)
        # export pdf
        pdf = self.client.get('/api/expenses/expenses/export/pdf/')
        self.assertEqual(pdf.status_code, 200)
        # update expense
        ue = self.client.put(f'/api/expenses/update/{exp_id}/', {'amount':'50.00'}, format='json')
        self.assertEqual(ue.status_code, 200)
        # delete expense
        de = self.client.delete(f'/api/expenses/delete/{exp_id}/')
        self.assertEqual(de.status_code, 200)
        # delete budget and category
        self.client.delete(f'/api/budgets/budgets/{bud_id}/delete/')
        self.client.delete(f'/api/budgets/delete/{cat_id}/')

    def test_dashboard_and_contact(self):
        # dashboard endpoints should all return 200 or message states no data
        endpoints = [
            '/api/dashboard/summary/',
            '/api/dashboard/analytics/trends/',
            '/api/dashboard/analytics/category-breakdown/',
            '/api/dashboard/analytics/budget-adherence/',
            '/api/dashboard/analytics/month-comparison/',
            '/api/dashboard/analytics/statistics/',
        ]
        for url in endpoints:
            r = self.client.get(url)
            self.assertIn(r.status_code, (200, 400))
        # contact form
        c = self.client.post('/api/contact/submit/', {
            'full_name':'John Doe',
            'email':'john@example.com',
            'subject':'Test',
            'message':'Hello there, this is at least ten chars.'
        }, format='json')
        if c.status_code not in (200, 201):
            print('contact response', c.status_code, c.data)
        # API returns 201 on success
        self.assertEqual(c.status_code, 201)

