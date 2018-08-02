"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Rating, Movie

from warnings import warn


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template("homepage.html")

@app.route('/users')
def user_list():
    """Show list of users."""

    users_list = User.query.all()
    return render_template("users.html", users=users_list)

@app.route('/users/<user_id>')
def display_user_info(user_id):

    #  Query user info with user_id
    user_info = User.query.filter(User.user_id == user_id).first()
    movie_ratings_by_user_id = Rating.query.filter(Rating.user_id == user_id).all()


    return render_template('user_info.html', user=user_info, movie_list=movie_ratings_by_user_id)

@app.route('/register', methods=["GET"])
def register_form():

    return render_template("register_form.html")

@app.route('/register', methods=["POST"])
def register_process():
    email = request.form['email']
    password = request.form['password']
    # check_user equals a single object
    # We are querying the database, and returning the first item that
    # has the same email that we input, because if it is in the db,
    # it will be the "first" one--if it's not in the db, will be None
    check_user = User.query.filter(User.email == email).first()

    # If the check_user variable above is None (the email does not)
    # exist in the db, then we want to add the new user
    if check_user is None:
        new_user = User(email = email, password = password)
        db.session.add(new_user)
        db.session.commit()
    else:
        print("Sorry! Can't do that.")
        # Figure out js-like alert for python? Flash message?

    return redirect('/')

@app.route('/login', methods=["GET"])
def login_form():

    return render_template("login_form.html")

@app.route('/login', methods=["POST"])
def login_process():

    # Data from form
    email = request.form['email']
    # print(email)
    password = request.form['password']
    # print(password)
    
    # Data queried from db
    user_in_db = User.query.filter(User.email == email).first()
    # print(user_in_db)
    user_password = user_in_db.password
    # print(user_password)
    user_id = user_in_db.user_id
    # print(user_id)

    if user_in_db is None:
        flash('Oops! You need to register first.')
        # print('Oops! You need to register first.')
    elif email == user_in_db.email and password == user_in_db.password:
        session['user_id'] = user_id
        flash('Yay! You are logged in.')
        # print('Yay! You are logged in.')


    return redirect('/users/' + str(user_id))

@app.route('/logout')
def logout_process():

    del session['user_id']
    flash('Thanks for logging out. Come back soon!')
    return redirect('/login')


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
