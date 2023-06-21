def init_data():
        from .. import db
        s = db.session()

        from ..db_models import Config
        config = Config.query.first()
        if config == None:
            new_config_1 = Config("rest_api_user", "admin")
            new_config_2 = Config("rest_api_pass", "!s/vm5Zut2PyCXOR")
            new_config_3 = Config("rest_api_ticketing_tool", "ServiceNow")
            new_config_4 = Config("rest_api_url", "https://dev126629.service-now.com")
            new_config_5 = Config("host_url", "")
            s.add(new_config_1)
            s.add(new_config_2)
            s.add(new_config_3)
            s.add(new_config_4)
            s.add(new_config_5)
            s.commit()

        from ..db_models import User
        user = User.query.first()
        if user == None:
            new_user = User(
                email="chris@aldred.cloud",
                password="sha256$HYEi1dfUYtJiK5ZU$0bde8f5e9a6ebb98a0a3a3d057ff84a737e2ffe877b4cd753903f7e40bf1dcbc",
                first_name="Chris",
                last_name="Aldred"
            )
            new_user.admin_flag = True
            new_user.approved_flag = True
            s.add(new_user)
            s.commit()

            new_user_2 = User(
                email="admin@email.com",
                password="sha256$fQBYKzsb8r2XZl0h$9f73104475986e7f385c80238ee77f0eb6a950bcfe0111bff405a086aa922d26",
                first_name="test",
                last_name="account"
            )
            new_user_2.admin_flag = True
            new_user_2.approved_flag = True
            s.add(new_user_2)
            s.commit()

        from ..db_models import Article
        article = Article.query.first()
        if article == None:
            with open('init_articles/1.html', 'r') as f:
                html_string = f.read()
            new_article = Article("How to install and open Adobe Photoshop", html_string, "Adobe, Software, Install", new_user.id)
            s.add(new_article)
            s.commit()

            with open('init_articles/2.html', 'r') as f:
                html_string = f.read()
            new_article = Article("How to run Adobe acrobat on PC", html_string, "Adobe, Acrobat, Software", new_user.id)
            s.add(new_article)
            s.commit()

            with open('init_articles/3.html', 'r') as f:
                html_string = f.read()
            new_article = Article("Fix water damaged USB drive", html_string, "USB, Fix, Water", new_user.id)
            s.add(new_article)
            s.commit()

            with open('init_articles/4.html', 'r') as f:
                html_string = f.read()
            new_article = Article("Email server overloaded solution", html_string, "Email, IMAP, POP3, slowness, overloaded", new_user.id)
            s.add(new_article)
            s.commit()

            with open('init_articles/5.html', 'r') as f:
                html_string = f.read()
            new_article = Article("Update user password in active directory", html_string, "Passwords, User, Account, Active Directory", new_user.id)
            s.add(new_article)
            s.commit()
        
        from ..db_models import Ticket
        ticket = Ticket.query.first()
        if ticket == None:
            new_ticket = Ticket('EXAMPLE_1', 'Admin', 'IMAP server is not responding', 'When trying to access Outlook we are getting a timeout and no response.')
            s.add(new_ticket)
            s.commit()

            new_ticket = Ticket('EXAMPLE_2', 'Admin', 'Cannot edit PDF\'s on work laptop', 'I want to edit a PDF however i do not have any application on my PC which can do so.')
            s.add(new_ticket)
            s.commit()

            new_ticket = Ticket('EXAMPLE_3', 'Admin', 'Spilt coffee on flash drive', 'Now when I plug it in the computer does not recognise it!')
            s.add(new_ticket)
            s.commit()

        from ..db_models import Task
        task = Task.query.first()
        if task == None:
            user = User.query.first()
            new_task = Task('Finish developing IKASA', 'Task description goes here', user, user)
            s.add(new_task)
            s.commit()