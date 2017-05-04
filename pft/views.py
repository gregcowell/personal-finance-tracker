"""Module that handles web views."""
from flask import render_template, url_for, request, redirect, session, flash,\
    Blueprint
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound
from .database import Transaction, Category, Business, Account, User
from .forms import ModifyTransactionForm
from .password import password_verified
from .database import db


web = Blueprint('web', __name__)


@web.route('/')
@web.route('/home')
def home_page():
    """Return Home HTML page."""
    if not session.get('logged_in'):
        return render_template('login.html')
    return render_template('home.html', user=session['user'],
                           login_time=session['login_time'], menu="home")


@web.route('/login', methods=['POST'])
def login():
    """Login and return Home HTML page."""
    try:
        user = db.session.query(User).\
            filter(User.username == request.form['username']).one()
    except NoResultFound:
        flash('Invalid login, please try again.')
        return home_page()
    if password_verified(request.form['password'], user.password):
        session['logged_in'] = True
        session['user'] = user.username
        session['login_time'] = datetime.utcnow()
    else:
        flash('Invalid login, please try again.')
    return home_page()


@web.route("/logout")
def logout():
    """Log out and return Home HTML page."""
    session['logged_in'] = False
    return home_page()


@web.route('/accounts')
def accounts_page():
    """Return Accounts HTML page."""
    if not session.get('logged_in'):
        return render_template('login.html')
    accounts = db.session.query(Account).\
        filter(Account.username == session['user']).\
        all()
    return render_template('accounts.html', accounts=accounts, menu="accounts")


@web.route('/transactions')
def transactions_page():
    """Return Transactions HTML page."""
    if not session.get('logged_in'):
        return render_template('login.html')
    transactions = db.session.query(Transaction, Category, Business, Account).\
        filter(Transaction.username == session['user']).\
        filter(Transaction.catno == Category.catno).\
        filter(Transaction.busno == Business.busno).\
        filter(Transaction.accno == Account.accno).\
        all()
    return render_template('transactions.html', transactions=transactions,
                           menu="transactions")


@web.route('/transactions/modify/<int:transno>/', methods=['GET', 'POST'])
def modify_transaction(transno):
    """
    Modify or delete transactions.

    Return a form for modifying transactions or process submitted
    form and redirect to Transactions HTML page.
    """
    if not session.get('logged_in'):
        return render_template('login.html')

    transaction = db.session.query(Transaction).\
        filter(Transaction.transno == transno).\
        one()
    businesses = db.session.query(Business).\
        filter(Business.username == session['user']).\
        all()
    categories = db.session.query(Category).\
        filter(Category.username == session['user']).\
        all()
    accounts = db.session.query(Account).\
        filter(Account.username == session['user']).\
        all()

    business_names = \
        [(business.busname, business.busname) for business in businesses]
    category_names = \
        [(category.catname, category.catname) for category in categories]
    account_names = \
        [(account.accname, account.accname) for account in accounts]

    form = ModifyTransactionForm()
    form.date.default = transaction.date
    form.business_name.choices = business_names
    form.business_name.default = transaction.business.busname
    form.category_name.choices = category_names
    form.category_name.default = transaction.category.catname
    form.account_name.choices = account_names
    form.account_name.default = transaction.account.accname
    form.amount.default = '{:,.2f}'.format(transaction.amount / 100)

    if form.validate_on_submit():
        if form.modify.data:
            transaction.date = form.date.data
            for business in businesses:
                if business.busname == form.business_name.data:
                    transaction.business = business
            for category in categories:
                if category.catname == form.category_name.data:
                    transaction.category = category
            for account in accounts:
                if account.accname == form.account_name.data:
                    transaction.account = account
            transaction.amount = form.amount.data * 100
            db.session.add(transaction)
            db.session.commit()
        elif form.delete.data:
            db.session.delete(transaction)
            db.session.commit()
        elif form.cancel.data:
            pass
        return redirect(url_for('.transactions_page'))

    form.process()  # Do this after validate_on_submit or breaks CSRF token

    return render_template('modify_transaction.html', form=form,
                           transno=transaction.transno, menu="transactions")


@web.route('/businesses')
def businesses_page():
    """Return Businesses HTML page."""
    if not session.get('logged_in'):
        return render_template('login.html')
    businesses = db.session.query(Business).\
        filter(Business.username == session['user']).\
        all()
    return render_template('businesses.html', businesses=businesses,
                           menu="businesses")


@web.route('/categories')
def categories_page():
    """Return Categories HTML page."""
    if not session.get('logged_in'):
        return render_template('login.html')
    categories = db.session.query(Category).\
        filter(Category.username == session['user']).\
        all()
    return render_template('categories.html', categories=categories,
                           menu="categories")


@web.route('/reports')
def reports_page():
    """Return reports HTML page."""
    if not session.get('logged_in'):
        return render_template('login.html')
    return render_template('reports.html', menu="reports")