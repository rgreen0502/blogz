from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'super_secret_key'
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    blog_title = ''
    blog_body = ''
    blog_title_error = ''
    blog_body_error = ''

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
            new_blog = Blog(blog_title,blog_body)
            db.session.add(new_blog)
            db.session.commit()
            post_link = "/blog?id=" + str(new_blog.id)
            return redirect(post_link)
        
        return redirect('/blog')

    return render_template('/newpost.html', a_title = 'Add a Blog', blog_title=blog_title, blog_body=blog_body, blog_title_error=blog_title_error, blog_body_error=blog_body_error)


@app.route('/blog')
def show_blog():
    post_id = request.args.get('id')
    if (post_id):
        post = Blog.query.get(post_id)
        return render_template('post.html',blog=post)
    else:
        all_blog_posts = Blog.query.all()
        return render_template('blog.html', blogs=all_blog_posts)

if __name__ == '__main__':
    app.run()


