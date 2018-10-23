from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'super_secret_key'
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'show_blog', 'index']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            return redirect('/blog')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

def empty_field(x):
    if x:
        return True
    else:
        return False

def char_length(x):
    if len(x)>2 and len(x)<21:
        return True
    else:
        return False

def at_symbol(x):
    if x.count("@") == 1:
        return True
    else:
        return False

def email_period(x):
    if x.count(".") == 1:
        return True
    else:
        return False


@app.route('/signup', methods=["POST", "GET"])
def signup():

    if request.method == 'POST':

        email = request.form["email"]
        password = request.form["password"]
        verify = request.form["verify"]
        email_error = ""
        password_error = ""
        verify_error = ""


        if not empty_field(email):
            email_error="Please enter an Email."

        elif not char_length(email):
            email_error="Must be between 3 and 20 characters."

        elif not email_period(email):
            email_error="Can only have one period!"

        elif not at_symbol(email):
            email_error="Enter a valid email address(with a @)!"

        else:
            if " " in email:
                email_error="No spaces allowed!"

        if not empty_field(password):
            password_error="Please enter a Password."
            email=email

        elif not char_length(password):
            password_error="Must be between 3 and 20 characters."
            email=email

        else:
            if " " in password:
                password_error="No spaces allowed!"
                email=email

        if verify != password:
            verify_error="Passwords must match."
            email=email

        if not email_error and not password_error and not verify_error:
            existing_user = User.query.filter_by(email=email).first()
            if not existing_user:
                new_user = User(email, password)
                db.session.add(new_user)
                db.session.commit()
                session['email'] = email
            return redirect('/newpost')
        return render_template("signup.html", email_error=email_error, email=email, password_error=password_error, password=password, verify=verify, verify_error=verify_error)
    else:
        return render_template("signup.html")
        
@app.route('/logout')
def logout():
    del session['email']
    return redirect('/login')    
                

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    blog_title = ''
    blog_body = ''

    blog_title_error = ''
    blog_body_error = ''

    owner = User.query.filter_by(email=session['email']).first()

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        if blog_title == '':
            blog_title_error = 'Please include a title.'
            return render_template('/newpost.html', blog_body=blog_body, blog_title_error=blog_title_error)
        
        elif blog_body == '':
            blog_body_error = 'Please include some thoughts!'
            return render_template('/newpost.html', blog_title=blog_title, blog_body_error=blog_body_error)

        else:
            new_blog = Blog(blog_title,blog_body,owner)
            #blogs = Blog.query.filter_by(owner=owner)
            db.session.add(new_blog)
            db.session.commit()
            post_link = "/blog?id=" + str(new_blog.id)
            return redirect(post_link)
        
        return redirect('/blog')

    return render_template('/newpost.html', a_title = 'Add a Blog', blog_title=blog_title, blog_body=blog_body, blog_title_error=blog_title_error, blog_body_error=blog_body_error)

@app.route('/blog')
def show_blog():

    owner = User.query.filter_by(email=session['email']).first()
    blog_id = request.args.get('id')
    if (blog_id):
        post = Blog.query.get(blog_id)
        return render_template('post.html',blog=post)
    else:
        all_blog_posts = Blog.query.filter_by(owner=owner)
        return render_template('blog.html', blogs=all_blog_posts)

@app.route('/')
def index():
    user_id = request.args.get('id')
    

if __name__ == '__main__':
    app.run()


