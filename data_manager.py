from models import db, User, Movie


class DataManager:

    @staticmethod
    def create_user(name):
        user = User(name=name)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_users():
        return User.query.all()

    @staticmethod
    def get_movies(user_id):
        return Movie.query.filter_by(user_id=user_id).all()

    @staticmethod
    def add_movie(movie):
        db.session.add(movie)
        db.session.commit()
        return movie

    @staticmethod
    def update_movie(movie_id, new_title):
        movie = Movie.query.get(movie_id)
        if movie:
            movie.name = new_title
            db.session.commit()
        return movie

    @staticmethod
    def delete_movie(movie_id):
        movie = Movie.query.get(movie_id)
        if movie:
            db.session.delete(movie)
            db.session.commit()
        return movie

    @staticmethod
    def update_user(user_id, new_name):
        user = User.query.get(user_id)
        if user:
            user.name = new_name
            db.session.commit()
        return user

    @staticmethod
    def delete_user(user_id):
        user = User.query.get(user_id)
        if user:
            Movie.query.filter_by(user_id=user.id).delete()
            db.session.delete(user)
            db.session.commit()
        return user
