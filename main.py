from website import create_app
from werkzeug.security import generate_password_hash

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)