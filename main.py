from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired, Length
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)
db = SQLAlchemy(app)

class Form(FlaskForm):
    rating = FloatField('Your Rating Out of 10 e.g. 7.5', validators=[DataRequired()])
    review = StringField('Your Review', validators=[DataRequired(), Length(max=250)])
    submit = SubmitField('Change')

class AddForm(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField('Add Movie')

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, unique=False, nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, unique=False, nullable=True)
    review = db.Column(db.String, unique=False, nullable=True)
    img_url = db.Column(db.String, unique=True, nullable=False)
db.create_all()

url = 'https://api.themoviedb.org/3/search/movie'
p = {
    'api_key': 'a02b6eabbccc690f05201fbf9ff520c3'
}


@app.route("/")
def home():
    movies = Movie.query.all()
    # in case if there is no data in movies.db
    try:
        ratings = sorted([i.rating for i in movies], reverse=True)
        for j in movies:
            for i in ratings:
                if i == j.rating:
                    rank = ratings.index(i) + 1
                    j.ranking = rank
        new_movies = sorted(movies, key=lambda x: x.ranking, reverse=True)

        return render_template("index.html", movies=new_movies)
    except:
        return render_template("index.html", movies=movies)

@app.route("/edit", methods=['GET', 'POST'])
def edit():
    form = Form()
    film_num = request.args.get('film_id')
    film = Movie.query.get(film_num)
    if form.validate_on_submit():
        film.rating = request.form['rating']
        film.review = request.form['review']
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", film=film, form=form)
@app.route("/delete")
def delete():
    film_num = request.args.get('film_id')
    film = Movie.query.get(film_num)
    db.session.delete(film)
    db.session.commit()
    return redirect(url_for('home'))
@app.route("/add", methods=['POST', 'GET'])
def add():
    form = AddForm()
    if form.validate_on_submit():
        p['query'] = request.form['title']
        req = requests.get(url=url, params=p).json()['results']
        return render_template('select.html', movies=req)
    return render_template('add.html', form=form)
@app.route("/select", methods=['POST', 'GET'])
def select():
    build_url = 'https://api.themoviedb.org/3/movie'
    id = '/' + request.args.get('film_id')
    film = requests.get(url=build_url + id, params={'api_key': 'a02b6eabbccc690f05201fbf9ff520c3'}).json()
    new_movie = Movie(
        title=film['title'],
        year=int(film['release_date'].split('-')[0]),
        description= film['overview'],
        rating=0,
        ranking=1,
        review='None',
        img_url=f"https://image.tmdb.org/t/p/w500{film['poster_path']}"
    )
    db.session.add(new_movie)
    db.session.commit()
    film = Movie.query.filter_by(title=film['title']).first()
    return redirect(url_for('edit', film_id=film.id))
if __name__ == '__main__':
    app.run(debug=True)

