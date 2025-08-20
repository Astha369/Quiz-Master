from werkzeug.security import generate_password_hash
from models.model import db, Admin
from flask import Flask, render_template
from controllers.database import db
# import controllers
from controllers.student import student_bp
from controllers.admin import admin_bp
from controllers.auth import auth_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_master.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your-secret-key'

db.init_app(app)

with app.app_context():
    db.create_all()
    existingAdmin = Admin.query.filter_by(username="admin").first()
    # generate admin credential
    if not existingAdmin:
        adminPassword = generate_password_hash("admin123", method='pbkdf2:sha256')
        newAdmin = Admin(username="admin", password=adminPassword)
        db.session.add(newAdmin)
        db.session.commit()
        
app.register_blueprint(student_bp, url_prefix='/student')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(auth_bp, url_prefix='/auth')
        
@app.route('/')
def home():
    return render_template('auth/signUpPage.html')

if __name__ == '__main__':
    app.run(debug=True)
