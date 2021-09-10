try:
    from main import app
    import unittest
    from urllib.parse import urlparse
    from random import randint

except Exception as e:
    print("Some modules are missing {}".format(e))

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

class FlaskTest(unittest.TestCase):

    ###################
    ### Login tests ###
    ###################

    # Check for response 200
    def test_login_status(self):
        tester = app.test_client(self)
        response = tester.get("/login")
        self.assertEqual(response.status_code, 200)
    
    # Check if content returned is html
    def test_login_content(self):
        tester = app.test_client(self)
        response = tester.get("/login")
        self.assertEqual(response.content_type, "text/html; charset=utf-8")

    # Check for data returned
    def test_login_data(self):
        tester = app.test_client(self)
        response = tester.get("/login")
        self.assertTrue(b'Login' in response.data)      
    
    # Check attempt to bypass login
    def test_login_bypass(self):
        tester = app.test_client(self)

        response = tester.get("/home")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, '/login')

        response = tester.get("/articles")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, '/login')

        response = tester.get("/tickets")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, '/login')

        response = tester.get("/user")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, '/login')

        response = tester.get("/admin")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, '/login')

    # Check unsuccessfull login
    def test_login_fail(self):
        tester = app.test_client(self)
        response = tester.post(
            '/login',
            data = dict(email='fake@fake.com', password='wrong'),
            follow_redirects=False
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Login' in response.data)
        self.assertFalse(b'Home' in response.data)
    
    # Check successfull login
    def test_login_success(self):
        tester = app.test_client(self)
        response = tester.post(
            '/login',
            data = dict(email='test@test.com', password='test123'),
            follow_redirects=False
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, '/home')
    
    # Check logout 
    def test_logout(self):
        tester = app.test_client(self)
        tester.post(
            '/login',
            data = dict(email='test@test.com', password='test123'),
            follow_redirects=False
        )
        response = tester.get('/logout')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, '/login')
        response = tester.get("/home")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, '/login')


    ########################
    ### Navigation tests ###
    ########################

    # Check pages return correct
    def test_navigation_success(self):
        tester = app.test_client(self)
        #Login
        tester.post(
            '/login',
            data = dict(email='test@test.com', password='test123'),
            follow_redirects=False
        )

        response = tester.get('/tickets')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'<h1 align="center">Tickets</h1>' in response.data)

        response = tester.get('/articles')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'<h1 align="center">Articles</h1>' in response.data)

        response = tester.get('/user')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'<h1 align="center">Account</h1>' in response.data)

        response = tester.get('/admin')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'<h1 align="center">Admin</h1>' in response.data)


    #####################
    ### Article tests ###
    #####################

    def test_add_article_logged_out(self):
        tester = app.test_client(self)
        response = tester.post(
            '/articles/add',
            data = dict(title='New article', editor='Description', tags='test, article'),
            follow_redirects=False
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, '/login')
    
    def test_add_article_success(self):
        tester = app.test_client(self)
        #Login
        tester.post(
            '/login',
            data = dict(email='test@test.com', password='test123'),
            follow_redirects=False
        )
        response = tester.post(
            '/articles/add',
            data = dict(title='New article ' + str(random_with_N_digits(5)), editor='Description', tags='test, article'),
            follow_redirects=False
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/articles/' in urlparse(response.location).path)
    
    def test_add_article_fail(self):
        tester = app.test_client(self)
        #Login
        tester.post(
            '/login',
            data = dict(email='test@test.com', password='test123'),
            follow_redirects=False
        )
        response = tester.post(
            '/articles/add',
            data = dict(title=None, editor='Description', tags='test, article'),
            follow_redirects=True
        )
        self.assertTrue(b'id="error-alert"' in response.data)   

    def test_delete_article_logged_out(self):
        tester = app.test_client(self)
        response = tester.post(
            '/articles/delete/1',
            data = None,
            follow_redirects = False
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, '/login')
    
    def test_delete_existing_article(self):
        tester = app.test_client(self)
        #Login
        tester.post(
            '/login',
            data = dict(email='test@test.com', password='test123'),
            follow_redirects=False
        )
        response = tester.post(
            '/articles/delete/2',
            data = None,
            follow_redirects = True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'id="success-alert"' in response.data)

    def test_delete_missing_article(self):
        tester = app.test_client(self)
        #Login
        tester.post(
            '/login',
            data = dict(email='test@test.com', password='test123'),
            follow_redirects=False
        )
        response = tester.post(
            '/articles/delete/99999',
            data = None,
            follow_redirects = True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'id="error-alert"' in response.data) 


    #####################
    ### Account tests ###
    #####################

    def test_update_details_success(self):
        tester = app.test_client(self)
        #Login
        tester.post(
            '/login',
            data = dict(email='test@test.com', password='test123'),
            follow_redirects=False
        )
        email_rand = 'test-email-' + str(random_with_N_digits(3)) + '@test.com'
        response = tester.post(
            '/user',
            data = dict(email=email_rand, firstName='Test', secondName='User', password1='1234567', password2='1234567'),
            follow_redirects=True
        )
        self.assertTrue(b'id="success-alert"' in response.data) 
        response = tester.post(
            '/user',
            data = dict(email='test@test.com', firstName='Test', secondName='User', password1='test123', password2='test123'),
            follow_redirects=True
        )
        self.assertTrue(b'id="success-alert"' in response.data)

    def test_update_details_failure(self):
        tester = app.test_client(self)
        #Login
        tester.post(
            '/login',
            data = dict(email='test@test.com', password='test123'),
            follow_redirects=False
        )

        email_rand = 'test-email-' + str(random_with_N_digits(3)) + '@test.com'
        response = tester.post(
            '/user',
            data = dict(email=email_rand, firstName='', secondName='User', password1='test123', password2='test123'),
            follow_redirects=True
        )
        self.assertTrue(b'id="error-alert"' in response.data)

        email_rand = 'test-email-' + str(random_with_N_digits(3)) + '@test.com'
        response = tester.post(
            '/user',
            data = dict(email=email_rand, firstName='Test', secondName='User', password1='', password2='test123'),
            follow_redirects=True
        )
        self.assertTrue(b'id="error-alert"' in response.data) 

        response = tester.post(
            '/user',
            data = dict(email='test@test.com', firstName='Test', secondName='User', password1='test123', password2='test123'),
            follow_redirects=True
        )
        self.assertTrue(b'id="success-alert"' in response.data) 


    ###################
    ### Admin tests ###
    ###################

    def test_admin_access_nonadmin_user(self):
        tester = app.test_client(self)
        #Login
        tester.post(
            '/login',
            data = dict(email='jezza@aldred.cloud', password='1234567'),
            follow_redirects=False
        )

        response = tester.get("/admin")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, '/home')

        response = tester.post(
            '/admin',
            data = None,
            follow_redirects=True
        )
        self.assertTrue(b'id="error-alert"' in response.data)

        response = tester.post(
            '/admin',
            data = dict(ticketing_tool="ServiceNow", API_URL="test.com", API_USER="admin", API_PASS="1234567"),
            follow_redirects=True
        )
        self.assertTrue(b'id="error-alert"' in response.data)
    
    def test_admin_access_no_login(self):
        tester = app.test_client(self)

        response = tester.get("/admin")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, '/login')

        response = tester.post(
            '/admin',
            data = None,
            follow_redirects=False
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, '/login')

        response = tester.post(
            '/admin',
            data = dict(ticketing_tool="ServiceNow", API_URL="test.com", API_USER="admin", API_PASS="1234567"),
            follow_redirects=False
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, '/login')
    
    def test_admin_update_success(self):
        tester = app.test_client(self)
        tester.post(
            '/login',
            data = dict(email='admin@email.com', password='Ikasa_admin123!'),
            follow_redirects=False
        )
    
        response = tester.get("/admin")
        self.assertEqual(response.status_code, 200)

        response = tester.post(
                '/admin',
                data = dict(ticketing_tool="ServiceNow", API_URL="test.com", API_USER="admin", API_PASS="1234567"),
                follow_redirects=True
            )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'id="success-alert"' in response.data)

        response = tester.post(
                '/admin',
                data = dict(ticketing_tool="ServiceNow", API_URL="", API_USER="", API_PASS=""),
                follow_redirects=True
            )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'id="success-alert"' in response.data) 


if __name__ == '__main__':
    unittest.main()
    tester = app.test_client(self)