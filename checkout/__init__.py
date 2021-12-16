from flask import Flask
from flask_cors import CORS

application = Flask(__name__)
CORS(application)

from checkout import accommodationCart,utilities,jobCart,qandACart,otherServicesCart, oldProductsCart