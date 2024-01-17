import os
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

# os.environ["API_MOVIE_KEY"] = "008a4fbf6b96eb793d92a8ece563da95"

MOVIE_TOKEN_ACCESS = os.environ.get("MOVIE_TOKEN_ACCESS")
API_MOVIE_KEY = os.environ.get("API_MOVIE_KEY")
API_MOVIE_END_POINT = "https://api.themoviedb.org/3/search/movie"
API_MOVIE_END_POINT_ID = "https://api.themoviedb.org/3/movie"
URL_FOR_IMAGE = "https://image.tmdb.org/t/p/w500"

"""
This is the command used to set the enviromental variable
setx API_MOVIE_KEY 'value'
"""






class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(15), unique=True , nullable=False)
    year = db.Column(db.Integer)
    description = db.Column(db.String(100))
    rating = db.Column(db.Integer)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String(50))
    img_url = db.Column(db.String(50))

with app.app_context():
    db.create_all()











@app.route("/", methods=["GET","POST"])
def index():
    """This function displayed all the movies from the database, sorted by it's rating,but then
    The loop for display the movies on a ranking depending its rating"""
    all_movies = db.session.execute(db.select(Movies).order_by(Movies.rating)).scalars().all()


    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - 1
        db.session.commit()

    return render_template("index.html", all_movies=all_movies)


@app.route("/find")
def find():
    """This functions gets the id from select.html, in the select.html the results from the api request
    are displayed. Then if everything it is okey, this functions redirects to update in order to modify
    the rating which the user gives and a brief description.
    """
    id = request.args.get("id")

    """This url is only to search by id"""
    URL_FOR_ID = f"{API_MOVIE_END_POINT_ID}/{id}"

    api_params = {
        "api_key": API_MOVIE_KEY,
    }

    response = requests.get(URL_FOR_ID, api_params)
    response.raise_for_status()
    data = response.json()


    title = data["original_title"]
    image = data["poster_path"]
    year = data["release_date"]
    description = data["overview"]


    new_movie = Movies(
        title=title,
        year=year,
        description=description,
        img_url = f"{URL_FOR_IMAGE}{image}",
    )


    db.session.add(new_movie)
    db.session.commit()

    return redirect(url_for('update', id=new_movie.id))








@app.route("/update", methods=["GET", "POST"])
def update():
    """This function updates the rating and review after finding the movie in the api request
    Once the user clicks a particular movie, the title , the image, the date release are directly
    add to the data base, but the ranking and the review do not, just because those two options
    changes depending on the user
    """
    id = request.args.get("id")

    class MyForm(FlaskForm):
        movie_rating = StringField("Your rating",validators=[DataRequired()])
        movie_review = StringField("Your review",validators=[DataRequired()])
        submit_but = SubmitField("Update", validators=[DataRequired()])

    form = MyForm()


    if form.validate_on_submit():

        """db.get_or_404 prevents an error if the database it is empty when the app it is run the first time"""
        movie_to_update = db.get_or_404(Movies,id)
        movie_to_update.rating = float(form["movie_rating"].data)
        movie_to_update.review = form["movie_review"].data
        db.session.commit()

        return redirect(url_for('index'))


    return render_template("update.html", form=form)






@app.route("/delete")
def delete():
    """This function deletes a movie,the id is passed in <a> in the index.html,
    once that is done it redirects to indexin order to update the page
    """
        movie_id = request.args.get("id")
        movie = db.get_or_404(Movies, movie_id)
        db.session.delete(movie)
        db.session.commit()
        return redirect(url_for("index"))






@app.route("/add", methods=["GET","POST"])
def add():
    """This functions adds display the results in index.html , so the user can select any of them, but
    the information of the movie  displays just the title and the date release.That's because movies
    has a unique name

    """
    class MyForm (FlaskForm):
        movie_title = StringField("Title", validators=[DataRequired()])
        sub_button = SubmitField("Add", validators=[DataRequired()])
    form = MyForm()

    if form.validate_on_submit():
        api_params = {
            "query" : form["movie_title"].data,
            "api_key": API_MOVIE_KEY,

        }
        response = requests.get(API_MOVIE_END_POINT, api_params)
        response.raise_for_status()
        data = response.json()

        result = data["results"]
        return render_template("select.html", result=result)

    return render_template("add.html", form=form)



















app.secret_key = "123"


if __name__ == "__main__":
    app.run(debug=True)