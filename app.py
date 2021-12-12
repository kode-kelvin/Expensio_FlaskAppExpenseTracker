from os import error
import json
from decouple import config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import login_required, login_user, LoginManager, logout_user, UserMixin,  current_user
from flask_wtf import FlaskForm, Form
from wtforms import StringField, SubmitField, PasswordField, BooleanField, DateField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
import datetime
from flask import  render_template, url_for, flash, redirect, session, request, jsonify
import uuid
from flask_mail import Mail, Message
from datetime import date, datetime, timedelta
# for web token
import jwt
from functools import wraps
import calendar
import time
import threading




app=Flask(__name__)
# settings config
app.config['SECRET_KEY'] = config('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expense.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False





# ----
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')

        if not token:
            return jsonify({'message':'Token is missing'}), 403

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            # return jsonify({"message":"Token is not valid"}), 403
            return redirect(url_for('errortoken'))
       
        return f(*args, **kwargs)
    return decorated

# sending an email
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] =  config('email')
app.config['MAIL_PASSWORD'] = config('password')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True


# email
mail = Mail(app)
# ini
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# login related
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))




# model -------    -------            --------------   ------- ------- -------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    money = db.relationship('Account', backref='author', lazy=True)
    budget = db.relationship('Budget', backref='author', lazy=True)
    public_id = db.Column(db.String(50), unique=True)

    def __repr__(self):
        return f"User('{self.username}','{self.email}', '{self.public_id}', '{self.money}', '{self.budget}')"


# their account
class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    money = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    entry_type = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    dt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    current_month = db.Column(db.Integer, nullable=True)
    day_month = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'Money("{self.money}", "{self.entry_type}", "{self.user_id}", "{self.description}", "{self.dt}", "{self.day_month}")'


# budget
class Budget(db.Model, UserMixin):
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    month = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    budget = db.Column(db.Integer, nullable=False, default=0)
    current_month = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"Budget('{self.id}', '{self.budget}', '{self.user_id}', '{self.month}', '{self.current_month}')"
        


# registration form -------    -------            --------------   ------- ------- -------
class RegistrationForm(FlaskForm): #registration form
    username = StringField('Username', validators=[DataRequired(), Length(min=5, max=20)])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken ! Please choose a different one')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken ! Please choose a different one')



class LoginForm(FlaskForm): #login form
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')





class BudgetForm(FlaskForm): #budget form 
    month = DateField('Budget Month', format="%m-%Y")
    budget = IntegerField('Projected Expenses', validators=[DataRequired()])
    submit = SubmitField('Create Budget')


#email all users in the database every 24hr
with app.app_context():
    def reminder():
        while 1:
            print("check something")
            subject = 'Your Daily Reminder'
            url = 'http://127.0.0.1:5000/'
            contacts = []
            users = User.query.all()
            for i in users:
                contacts.append(i.email)
            msg = Message(subject, sender='noreply@demo.com', recipients=contacts)
            msg.body = f"Hello Esteem User, hope you have a great day today. Do remember to log your transaction today {url}"
            mail.send(msg)
            dt = datetime.now() + timedelta(hours=1)
            dt = dt.replace(minute=10)

            while datetime.now() < dt:
                time.sleep(1)
  
        threading.Thread(target=reminder).start()

# routes ----- -- ----- -- ---- URLS  -------    -------            --------------   ------- ------- -------
@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, public_id=str(uuid.uuid4()))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)


# login
@app.route('/login', methods=['POST', 'GET'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login failed, check password and email')
    return render_template('signin.html', form=form)
        
# dash

@app.route('/', methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        entry_amount = request.form['amount']
        description = request.form['description']
        entry_type = request.form['status']
        if not entry_amount:
            flash('You must enter an amount', category='error')
        if not description:
            flash('You must enter a description', category='error')
        else:
            new_entry = Account(money=entry_amount, description=description, entry_type=entry_type, author=current_user, current_month=datetime.now().strftime("%m"),day_month=datetime.now().strftime("%A"))
            db.session.add(new_entry)
            db.session.commit()
            flash('Entry created', category='info')
    
    user_account = User.query.filter_by(username=current_user.username).first()
    account_balance = Account.query.filter_by(author=current_user, entry_type="credit").all()
    cash =  (sum([fund.money for fund in account_balance]))
    # debit
    account_debit = Account.query.filter_by(author=current_user, entry_type="debit").all()
    debit_cash =  (sum([fund.money for fund in account_debit]))

    # the real balance
    current_balance = cash - debit_cash
    #
    page = request.args.get('page', 1, type=int)
    all_cash = Account.query.filter_by(author=current_user).order_by(Account.dt.desc()).paginate(page=page, per_page=4)
    return render_template('app.html', data=user_account, cash=cash, debit_cash=debit_cash, balance=current_balance, all_cash=all_cash)



# logout - ----- -- -
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/delete/<int:id>')
@login_required
def delete(id):
    cash = Account.query.get_or_404(id)
    db.session.delete(cash)
    db.session.commit()
    return redirect('/')


reset_link = 'http://127.0.0.1:5000/passwordreset?token='

@app.route('/forgetpassword', methods=['GET', 'POST']) 
def forgotPassword():
    if request.method == 'POST':
        email = request.form['email']
        if not email:
            flash('You need to enter your email', category=error)
        if User.query.filter_by(email=email).first():
            token = token = jwt.encode({'user' : email, 'exp' : datetime.utcnow() + timedelta(seconds=60)}, app.config['SECRET_KEY'])
            token = {"token":token.decode('UTF-8')}
            # send welcome email
            subject = 'Request token'
            msg = Message(subject, sender='noreply@demo.com', recipients=[email]) # form.email.data
            msg.body = f"Follow this link to reset your password{reset_link}{token['token']}"
            mail.send(msg)
            flash('Follow reset link in your email')
        else:
            flash('The email does not exist')
    return render_template('forgotpass.html')

     
# Rest the password   ------- 
@app.route('/passwordreset', methods =['GET', 'POST'])
@token_required
def passwordreset():
    token = request.args.get('token')
    user_info = jwt.decode(token, app.config['SECRET_KEY'])
    user_email = user_info['user']
    
    if request.method == 'POST':
        req_user = User.query.filter_by(email=user_email).first()
        new_password = request.form['password']
        confirm_password = request.form['confirm_password']

        if not confirm_password and not new_password:
            flash('You have to fill out all fields')
        if new_password != confirm_password:
            flash('Your password did not match')
        
        else:
            req_user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            db.session.commit()
            flash('Your successful changed')
            return redirect(url_for('login'))
    return render_template('newpass.html')


# expired token
@app.route('/errortoken')
def errortoken():
    flash('Error occurred, either token expired or missing token', category="error")
    return render_template('error.html')



# ---- dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    income_vs_expenses = db.session.query(db.func.sum(Account.money), Account.entry_type).group_by(Account.entry_type).order_by(Account.entry_type).all()

    income_expense = []
    for total_amount, _ in income_vs_expenses:
        income_expense.append(total_amount)

  

    # query over period of time
    dates = db.session.query(db.func.sum(Account.money), Account.dt).group_by(Account.dt).order_by(Account.dt).all()
    over_time = []
    time_labels = []
    for amount, date in dates:
        over_time.append(amount)
        time_labels.append(date.strftime("%m-%d-%y"))

    return render_template('dashboard.html', income_vs_expenses=json.dumps(income_expense),
    over_time_spent=json.dumps(over_time),
    over_time_label=json.dumps(time_labels)  
    )


# budget ---
@app.route('/createbudget', methods=['POST', 'GET'])
@login_required
def createBudget():

    # creating the budget
    form = BudgetForm()
    if form.validate_on_submit():
        new_budget = Budget(month=form.month.data, budget=form.budget.data, author=current_user, current_month=form.month.data.strftime("%m"))
        db.session.add(new_budget)
        db.session.commit()
        flash(f'Budget for {form.month.data.strftime("%B")} created successfully', category="info")

    # displaying all budgets
    budgets = Budget.query.filter_by(author=current_user).all()

    # displaying the budget for current month
    present_month = Budget.query.filter_by(author=current_user, current_month=datetime.now().strftime("%m")).all()
    cash = (sum([fund.budget for fund in present_month]))


    # getting all debit for the current month
    expense_for_month = Account.query.filter_by(author=current_user, entry_type="debit", current_month=datetime.now().strftime("%m")).all()
    cashy= (sum([fund.money for fund in expense_for_month]))
    
    session['cashy'] = cashy
   
    return render_template('budget.html', form=form, user_budget=budgets, present_month=present_month, cash=cash, cashy=cashy)



# budget details ----
@app.route('/budget/<int:id>', methods=['POST', 'GET'])
@login_required
def budgetDetails(id):
    # pulling data
    bud_det = Budget.query.get_or_404(id)

    # ---- updating budget
    if request.method =="POST":
        updateBud = request.form['amount']
        if not updateBud:
            flash("You must enter a budget", category="error")
        
        if int(updateBud) < bud_det.budget:
            flash("The budget you entered is lower than previous budget for this month", category="error")
        
        else:
            bud_det.budget = updateBud
            db.session.commit()

    # getting the expense for selected month
    expense_for_month = Account.query.filter_by(author=current_user, entry_type="debit", current_month=bud_det.current_month).all()
    total_debit = (sum([fund.money for fund in expense_for_month]))

    # query over period of time
    monthspend = db.session.query(db.func.sum(Account.money), Account.description).group_by(Account.description).order_by(Account.description).filter_by(author=current_user, entry_type="debit", current_month=bud_det.current_month).all()
    over_time = []
    time_labels = []
    for amount, description in monthspend:
        over_time.append(amount)
        time_labels.append(description)
    

    # query over period of time
    dates = db.session.query(db.func.sum(Account.money), Account.dt).group_by(Account.dt).order_by(Account.dt).filter_by(author=current_user, entry_type="debit", current_month=bud_det.current_month).all()
    overtime = []
    timelabels = []
    for amount, date in dates:
        overtime.append(amount)
        timelabels.append(date.strftime("%d/%m"))
    
    # ---- grouping by days
    spend = db.session.query(db.func.sum(Account.money), Account.day_month).group_by(Account.day_month).order_by(Account.day_month).filter_by(author=current_user, entry_type="debit", current_month=bud_det.current_month).all()

    time_over = []
    labels = []
    for total, day in spend:
        time_over.append(total)
        labels.append(day)

    return render_template('details.html', bud_det=bud_det, expense_for_month=expense_for_month, debit_list=json.dumps(over_time), debit_label=json.dumps(time_labels), total_debit=total_debit, day_time=json.dumps(overtime), day_labels=json.dumps(timelabels), time_over=json.dumps(time_over), labels=json.dumps(labels) )


# monthly spending
@app.route('/monthexpenses', methods=['GET', 'POST'])
@login_required
def monthexpense():
    from month_num import months_list
    months  = months_list
    

    if request.method == 'POST':
        name = request.form['month']
        month_name = calendar.month_name[int(name)]

        expense_for_selected_month = Account.query.filter_by(author=current_user, current_month=int(name)).all()
        total_spending = (sum([fund.money for fund in expense_for_selected_month ]))
        return render_template('month.html', months=months, name=month_name, selected_month=expense_for_selected_month, total_spending=total_spending )
    
    return render_template('month.html', months=months)









 #Run app------- 
if __name__ == '__main__':
    app.run(debug=True)


