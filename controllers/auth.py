from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from models.model import Admin, User
from controllers.database import db
from werkzeug.security import check_password_hash
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/adminLogin', methods=['GET', 'POST'])
def adminLogin():
    if request.method == 'POST':
        username = request.form.get('adminUsername')
        password = request.form.get('adminPassword')
        
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password, password):
            session['admin_id'] = admin.id
            flash('Admin logged in successfully!', "success")
            return redirect(url_for('admin.adminDashboard'))
        else:
            flash('Invalid username or password!', "danger")
            return redirect(url_for('auth.adminLogin'))
        
    return render_template('auth/adminLoginPage.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('studentUsername')
        password = request.form.get('studentPassword')
        name = request.form.get('studentName')
        qualification = request.form.get('studentQualification')
        dobInString = request.form.get('studentDOB')
        
        userExists = User.query.filter_by(username=username).first()
        if userExists:
            flash("Username already exists", "danger")
            return redirect(url_for('auth.signup'))
        
        dob = datetime.strptime(dobInString, '%Y-%m-%d').date()
        
        newUser = User(
            username=username,
            password=password,
            fullName=name,
            qualification=qualification,
            dOB=dob
        )

        db.session.add(newUser)
        db.session.commit()
        
        flash("Registration is successful! Please log in...", "success")
        return redirect(url_for('auth.studentLogin'))
    return render_template('auth/signUpPage.html')

@auth_bp.route('/studentLogin', methods=['GET', 'POST'])
def studentLogin():
    if request.method == 'POST':
        username = request.form.get('studentUsername')
        password = request.form.get('studentPassword')
        
        user = User.query.filter_by(username=username, password=password).first()
        
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Logged in successfully', "success")
            return redirect(url_for('student.studentDashboard'))
        
        else:
            flash("Invalid username or password. Please try again!", "danger")
            return redirect(url_for('auth.studentLogin'))
    return render_template('auth/studentLoginPage.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully", "info")
    return redirect(url_for('auth.studentLogin'))
