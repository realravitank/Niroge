
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime

bcrypt = Bcrypt()
db = SQLAlchemy()


class User(db.Model):
    """User Data."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    name = db.Column(
        db.Text,
        nullable=False,
        unique=False,
    )

    sex = db.Column(
        db.Text,
        nullable=False,
        unique=False,
    )
    
    unit = db.Column(
        db.Text,
        nullable=False,
        unique=False,
    )

    age = db.Column(
        db.Integer,
        nullable=False,
        unique=False,
    )

    goal = db.Column(
        db.Text,
        nullable=False,
        unique=False,
    )

    activity = db.Column(
        db.Text,
        nullable=False,
        unique=False,
    )
    
    weight = db.Column(
        db.Integer,
        nullable=False,
        unique=False,
    )

    goal_weight = db.Column(
        db.Integer,
        nullable=False,
        unique=False,
    )

    height = db.Column(
        db.Integer,
        nullable=False,
        unique=False,
    )

    rate = db.Column(
        db.Text,
        nullable=False,
        unique=False,
    )

    diet_type = db.Column(
        db.Text,
        nullable=False,
        unique=False,
    )

    budget = db.Column(
        db.Integer,
        nullable=True,
        unique=False,
    )


    meal = db.relationship('Meal')
    

    def __repr__(self):
        return f"<User #{self.id}: {self.name}, {self.email}>"


    @classmethod
    def signup(cls, email, password, name, unit, sex, age, goal, goal_weight, activity, height, weight, rate, diet_type, budget):

        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            email=email,
            password=hashed_pwd,
            name=name,
            sex=sex,
            unit=unit,
            age=age,
            goal=goal,
            goal_weight=goal_weight,
            activity=activity,
            height=height,
            weight=weight,
            rate=rate,
            diet_type=diet_type,
            budget=budget,
        )

        db.session.add(user)
        return user
    
    @classmethod
    def authenticate(cls, email, password):
        """Find user with `email` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(email=email).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

class Calorie(db.Model):

    """Calorie Data."""

    __tablename__ = 'calories'

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

    calories = db.Column(
        db.Integer,
        nullable = False,
    )


class Meal(db.Model):
    """Meal Data."""

    __tablename__ = 'meals'

    id = db.Column(
        db.Integer,
        primary_key=True,
        nullable=False,
        unique=True,
    )

    name = db.Column(
        db.Text,
        nullable=False,
        unique=False,
    )

    calories = db.Column(
        db.Integer,
        nullable=False,
        unique=False,
    )

    protien = db.Column(
        db.Text,
        nullable=False,
        unique=False,
    )

    fat = db.Column(
        db.Text,
        nullable=False,
        unique=False,
    )

    carbohydrate = db.Column(
        db.Text,
        nullable=False,
        unique=False,
    )

    price = db.Column(
        db.Text,
        nullable=False,
        unique=False,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow(),
    )


    user = db.relationship('User')


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)
