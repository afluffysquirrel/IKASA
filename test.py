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

        


if __name__ == '__main__':
    unittest.main()
    tester = app.test_client(self)