# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)

api = Api(app)

movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')


@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        director_id = request.args.get("director_id")
        if director_id:
            movie_director = db.session.query(Movie).filter(Movie.director_id == director_id).all()

            if type(movie_director) == list:
                return movies_schema.dump(movie_director), 200
            else:
                return movie_schema.dump(movie_director), 200

        genre_id = request.args.get("genre_id")
        if genre_id:
            movie_genre = db.session.query(Movie).filter(Movie.genre_id == genre_id).all()
            if type(movie_genre) == list:
                return movies_schema.dump(movie_genre), 200
            else:
                return movie_schema.dump(movie_genre), 200

        all_movies = Movie.query.all()
        return movies_schema.dump(all_movies), 200

    def post(self):
        req_json = request.json
        if not req_json:
            return "", 404
        new_movie = Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movie)
        return "", 201


@movie_ns.route('/<int:uid>')
class MovieView(Resource):
    def get(self, uid):
        movie = Movie.query.get(uid)
        return movie_schema.dump(movie), 200

    def delete(self, uid):
        movie = Movie.query.get(uid)
        if not movie:
            return "", 404
        db.session.delete(movie)
        db.session.commit()
        return "", 204

    def put(self, uid):
        req_json = request.json
        movie_uid = Movie.guery.get(uid)
        if not movie_uid:
            return "", 404
        movie_uid.title = req_json.get("title")
        movie_uid.description = req_json.get("description")
        movie_uid.trailer = req_json.get("trailer")
        movie_uid.year = req_json.get("year")
        movie_uid.rating = req_json.get("rating")
        movie_uid.genre_id = req_json.get("genre_id")
        movie_uid.director_id = req_json.get("director_id")

        db.session.add(movie_uid)
        db.session.commit()
        return "", 204


@director_ns.route('/')
class DirectorView(Resource):
    def get(self):
        directors_all = Director.query.all()
        return directors_schema.dump(directors_all), 200


@director_ns.route('/<int:uid>')
class DirectorView(Resource):
    def get(self, uid):
        director = Director.query.get(uid)
        return director_schema.dump(director), 200


@genre_ns.route('/')
class GenreView(Resource):
    def get(self):
        genres_all = Genre.query.all()
        return genres_schema.dump(genres_all), 200


@genre_ns.route('/<int:uid>')
class GenreView(Resource):
    def get(self, uid):
        movie_by_genre = db.session.query(Movie).filter(Movie.genre_id == uid).all()
        if movie_by_genre:
            if type(movie_by_genre) == list:
                return movies_schema.dump(movie_by_genre), 200
            else:
                return movie_schema.dump(movie_by_genre), 200
        return "", 404


if __name__ == '__main__':
    app.run(debug=True)
