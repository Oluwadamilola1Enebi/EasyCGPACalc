from flask import Flask, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
import os
from functools import wraps
from flask import abort

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import AddCourseForm, RegisterForm, LoginForm, SemesterForm


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URI','sqlite:///easycgpacalc.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#CONFIGURE LOGIN MANAGER
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#CREATE RELATIONAL DATABASE
Base= declarative_base()

##CONFIGURE TABLES
#USER TABLE
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    # This will act like a List of BlogPost objects attached to each User.
    # The "author" refers to the author property in the BlogPost class.
    semesters = relationship("Semester", back_populates="student")


#SEMESTER TABLES
class Semester(db.Model):
    __tablename__ = "semesters"
    id = db.Column(db.Integer, primary_key=True)
    semester_name = db.Column(db.String(1000))
    date_added = db.Column(db.String(250), nullable=False)
    gpa = db.Column(db.Float)
    num_courses = db.Column(db.Integer)
    course_units_sum = db.Column(db.Integer)
    grades_units_total = db.Column(db.Integer)
    present_cgpa = db.Column(db.Float)

    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # Create reference to the User object, the "posts" refers to the posts property in the User class.
    student = relationship("User", back_populates="semesters")



db.create_all()

with app.app_context():
    db.create_all()




U_LIST = []
G_LIST = []
AGG = []



@app.route('/')
def home():
    global U_LIST
    global G_LIST
    global AGG
    U_LIST = []
    G_LIST = []
    AGG = []
    return render_template("index.html", logged_in=current_user.is_authenticated, current_user=current_user)

@app.route('/register', methods=['GET','POST'])
def register():
    form=RegisterForm()
    if form.validate_on_submit():
        # FIRST, CHECK TO SEE IF EMAIL IS ALREADY IN RECORD
        if User.query.filter_by(email=form.email.data).first():
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        # CREATE RECORD
        plaintext_password = form.password.data
        new_user = User(
            email=form.email.data,
            password=generate_password_hash(plaintext_password, method='pbkdf2:sha256', salt_length=8),
            name=form.name.data

        )
        db.session.add(new_user)
        db.session.commit()
        # Log in and authenticate user after adding details to database.
        flash("Your email address has been registered, you can now log in!")
        return redirect(url_for('login'))
    return render_template("register.html", form=form, logged_in=current_user.is_authenticated)


@app.route('/login', methods=['POST','GET'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        # Find user by email entered.
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("This email is not registered. Please try again.")
            return redirect(url_for('login'))
        # Check stored password hash against entered password hashed.
        if check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('user_page'))
        else:
            flash("Password incorrect.Please try again.")
            return redirect(url_for('login'))
    return render_template("login.html", form=form, logged_in=current_user.is_authenticated)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/refresh", methods=['GET','POST'])
def refresh_page():
    global U_LIST
    global G_LIST
    global AGG
    U_LIST = []
    G_LIST = []
    AGG = []
    return redirect(url_for("add_new_course"))

@app.route("/undo", methods=['GET','POST'])
def undo():
    global U_LIST
    global G_LIST
    if len(U_LIST) > 0:
        del U_LIST[-1]
    if len(G_LIST) > 0:
        del G_LIST[-1]
    return redirect(url_for("add_new_course"))

@app.route("/enter-course", methods=['GET','POST'])
def add_new_course():
    global U_LIST
    global G_LIST
    global AGG
    num_c = len(U_LIST)
    form = AddCourseForm()

    if request.method == 'POST' and form.validate_on_submit():
        if form.next.data:
            units = form.course_units.data
            grade = form.course_grade.data
            U_LIST.append(units)
            if grade == 'A':
                G_LIST.append(5)
            elif grade == 'B':
                G_LIST.append(4)
            elif grade == 'C':
                G_LIST.append(3)
            elif grade == 'D':
                G_LIST.append(2)
            elif grade == 'E':
                G_LIST.append(1)
            else:
                G_LIST.append(0)
            return redirect(url_for("add_new_course"))


        if form.submit.data:
            units = form.course_units.data
            grade = form.course_grade.data
            U_LIST.append(units)
            if grade == 'A':
                G_LIST.append(5)
            elif grade == 'B':
                G_LIST.append(4)
            elif grade == 'C':
                G_LIST.append(3)
            elif grade == 'D':
                G_LIST.append(2)
            elif grade == 'E':
                G_LIST.append(1)
            else:
                G_LIST.append(0)
            for index, i in enumerate(G_LIST):
                num = i * U_LIST[index]
                AGG.append(num)
            GPA = round(sum(AGG) / sum(U_LIST), 4)


            if current_user.is_authenticated:
                # FOR COLLECTING USER'S RESULTS TO ADD TO DATABASE
                new_semester = Semester(
                    semester_name='Untitled',
                    date_added=date.today().strftime("%B %d, %Y"),
                    gpa=GPA,
                    num_courses=len(AGG),
                    course_units_sum=sum(U_LIST),
                    grades_units_total=sum(AGG),
                    present_cgpa=0.00,
                    student_id=current_user.id,
                    student=current_user
                )
                db.session.add(new_semester)
                db.session.commit()
                U_LIST = []
                G_LIST = []
                AGG = []
                return redirect(url_for("display_result_int", gpa=GPA, semester_id=new_semester.id))

            else:
                U_LIST = []
                G_LIST = []
                AGG = []
                return redirect(url_for("display_result_float", gpa=GPA))

    return render_template("enter-course.html", form=form, current_user=current_user, logged_in=current_user.is_authenticated, num=num_c)


@app.route("/result<int:semester_id><float:gpa>", methods=['GET','POST'])
def display_result_int(semester_id,gpa):
    semester = Semester.query.get(semester_id)
    grade_point_ave = gpa
    return render_template("result.html", current_user=current_user,logged_in=current_user.is_authenticated, semester=semester, gpa=grade_point_ave)

@app.route("/result<float:gpa>", methods=['GET','POST'])
def display_result_float(gpa):
    grade_point_ave = gpa
    return render_template("result.html", current_user=current_user,logged_in=current_user.is_authenticated, gpa=grade_point_ave)


@app.route('/your-page', methods=['GET','POST'])
@login_required
def user_page():
    for semester in current_user.semesters:
        if semester.semester_name=='Untitled':
            db.session.delete(semester)
            db.session.commit()
    return render_template("your-page.html", current_user=current_user,logged_in=current_user.is_authenticated)

@app.route("/delete/<int:semester_id>")
@login_required
def delete_semester(semester_id):
    semester_to_delete = Semester.query.get(semester_id)
    db.session.delete(semester_to_delete)
    db.session.commit()
    return redirect(url_for('user_page'))


@app.route('/save<int:semester_id>', methods=['GET','POST'])
@login_required
def save(semester_id):
    form=SemesterForm()
    last_semester = Semester.query.get(semester_id)

    CU_LIST=[]
    CAGG_LIST=[]
    for semester in current_user.semesters:
        CU_LIST.append(semester.course_units_sum)
        CAGG_LIST.append(semester.grades_units_total)
    try:
        cgpa = round((sum(CAGG_LIST)) / (sum(CU_LIST)), 4)
    except:
        cgpa=last_semester.gpa

    if request.method == 'POST' and form.validate_on_submit():
        last_semester.semester_name = form.semester_name.data
        last_semester.present_cgpa = cgpa
        db.session.commit()
        return redirect(url_for("user_page"))

    return render_template("semester.html", form=form, logged_in=current_user.is_authenticated, current_user=current_user)




if __name__ == "__main__":
    app.run(debug=True)
