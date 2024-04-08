from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField  #para aceptar texto imagen links etc
from datetime import date


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
ckeditor = CKEditor(app)

# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    db.create_all()


class AddPostForm(FlaskForm):
    title = StringField('The blog post title', validators=[DataRequired()])
    subtitle = StringField('The subtitle', validators=[DataRequired()])
    author = StringField("The author's name", validators=[DataRequired()])
    img_url = StringField("A URL for the background image", validators=[DataRequired(), URL()])
    body = CKEditorField("The body of the post", validators=[DataRequired()])
    submit = SubmitField('Submit Post')

@app.route('/')
def get_all_posts():
    # TODO: Query the database for all the posts. Convert the data to a python list.
    post = db.session.execute(db.select(BlogPost)).scalars().all()
    return render_template("index.html", all_posts=post)

# TODO: Add a route so that you can click on individual posts.
@app.route('/post/<int:post_id>',  methods = ['POST', 'GET'])
def show_post(post_id):
    # TODO: Retrieve a BlogPost from the database based on the post_id
    requested_post = db.session.execute(db.select(BlogPost).where(BlogPost.id==post_id)).scalar()
    return render_template("post.html", post=requested_post)


# TODO: add_new_post() to create a new blog post

@app.route('/new-post', methods = ['POST', 'GET'])
def new_post():
    form = AddPostForm()
    if form.validate_on_submit():
        new_post_entry = BlogPost(
            title = form.title.data,
            subtitle = form.subtitle.data, 
            author = form.author.data,
            img_url = form.img_url.data, 
            body = form.body.data,
            date = date.today().strftime('%B %d, %Y')
        )
        db.session.add(new_post_entry)
        db.session.commit()
        return redirect(url_for('get_all_posts'))
        
    return render_template('make-post.html', form = form)


# TODO: edit_post() to change an existing blog post

@app.route('/edit-post/<int:post_id>',  methods = ['POST', 'GET'])
def edit_post(post_id):
    post = db.session.execute(db.select(BlogPost).where(BlogPost.id==post_id)).scalar()
    edit_form = AddPostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    ) #para colocar los valores que actualmente tiene el post
    if edit_form.validate_on_submit():
            post.title = edit_form.title.data #editar los datos que ya estas sin crear nuevos id
            post.subtitle = edit_form.subtitle.data
            post.author = edit_form.author.data
            post.img_url = edit_form.img_url.data
            post.body = edit_form.body.data
            db.session.commit()
            return redirect(url_for('show_post', post_id=post_id))
    return render_template('make-post.html', form = edit_form, edit = True)

# TODO: delete_post() to remove a blog post from the database

@app.route('/delete/<post_id>')
def delete(post_id):
    post_delete = db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id)).scalar()
    db.session.delete(post_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))   
    

# Below is the code from previous lessons. No changes needed.
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5003)
