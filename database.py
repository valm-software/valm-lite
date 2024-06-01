from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.orm import relationship

db = SQLAlchemy()

def init_app(app):
   
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://javiercl:Madrid2020@191.96.251.40:4406/bd_valm_lite-202406010337'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://javiercl:Madrid2020@191.96.251.40:4406/bd_valm_lite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)