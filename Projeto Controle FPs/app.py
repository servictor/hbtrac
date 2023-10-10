import os
from flask import Flask, render_template
from routes import pages
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__,static_folder="estatico")
    app.register_blueprint(pages)
    client= MongoClient(os.environ.get("MONGODB_URI"))
    app.db=client.fpblog
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('not-found.html'), 404
    return app