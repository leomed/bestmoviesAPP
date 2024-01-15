from flask import Flask, render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
import requests

db = SQLAlchemy()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies-collection.db"
db.init_app(app)


TOKEN_ACCESS = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwMDhhNGZiZjZiOTZlYjc5M2Q5MmE4ZWNlNTYzZGE5NSIsInN1YiI6IjY1YTUwNTQwMGYyYWUxMDEyZDViMzg1YiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.rIIztOdrOFL8pNag5NvlhNk5HFvAdoB9R44Z4jJVX84"
API_KEY = "008a4fbf6b96eb793d92a8ece563da95"
API_END_POINT = "https://api.themoviedb.org/3/search/movie"




class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(15), unique=True , nullable=False)
    year = db.Column(db.Integer)
    description = db.Column(db.String(50))
    rating = db.Column(db.Integer)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String(50))
    img_url = db.Column(db.String(50))

with app.app_context():
    db.create_all()






@app.route("/")
def index():
    all_movies = db.session.execute(db.select(Movies).order_by(Movies.rating)).scalars()

    return render_template("index.html", all_movies=all_movies)






@app.route("/update/<id>", methods=["GET","POST"])
def update(id):
    class MyForm(FlaskForm):
        movie_rating = StringField("Your rating",validators=[DataRequired()])
        movie_review = StringField("Your review",validators=[DataRequired()])
        submit_but = SubmitField("Update", validators=[DataRequired()])

    form = MyForm()


    if form.validate_on_submit():
        movie_to_update = db.session.execute(db.select(Movies).where(Movies.id == id)).scalar()
        movie_to_update.rating = form["movie_rating"].data
        movie_to_update.review = form["movie_review"].data
        db.session.commit()

        return redirect(url_for('index'))
    return render_template("update.html", form=form)







@app.route("/delete/<id>")
def delete(id):
        id = request.args.get("id")
        movie = db.get_or_404(Movies, id)
        db.session.delete(movie)
        db.session.commit()
        return redirect(url_for("index"))









@app.route("/add", methods=["GET","POST"])
def add():


    class MyForm (FlaskForm):
        movie_title = StringField("Title", validators=[DataRequired()])
        sub_button = SubmitField("Add", validators=[DataRequired()])
    form = MyForm()
    if form.validate_on_submit():

        api_params = {
            "query" : form["movie_title"].data,
            "api_key": API_KEY,

        }
        response = requests.get(API_END_POINT, api_params)
        response.raise_for_status()
        data = response.json()

        result = data["results"]
        return render_template("select.html", result=result)

    return render_template("add.html", form=form)















app.secret_key = "123"


if __name__ == "__main__":
    app.run(debug=True)