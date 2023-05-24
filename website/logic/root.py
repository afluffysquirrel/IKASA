from flask import Blueprint
from flask.helpers import url_for
from werkzeug.utils import redirect

rootBluePrint = Blueprint('root', __name__)

# Home
@rootBluePrint.route('/', methods=['GET'])
def root():
    return redirect(url_for('home.home'))