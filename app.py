import os

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
import requests 

from forms import AddUserForm, EditUserForm, LoginForm, SignUpForm, EditUserWeightForm, AddMealForm
from models import db, connect_db, User, Meal, Calorie
import json

from datetime import datetime, date, timedelta

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'postgres:///niroge')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")

connect_db(app)

@app.before_request
def add_user_to_g():

    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]



@app.route('/', methods=["GET", "POST"])
def intro():
    """Handle index/login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.email.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.name}!", "success")
            return redirect(f"/home/{user.id}")

        flash("Invalid credentials.", 'danger')

    if g.user:
        return redirect(f"/home/{session[CURR_USER_KEY]}")
    return render_template('index.html', form=form)



@app.route('/goals', methods=["GET", "POST"])
def goals():
    """Handle user Goals."""

    form = AddUserForm()
    
    def calculate_age(dtob):
        today = date.today()
        return today.year - dtob.year - ((today.month, today.day) < (dtob.month, dtob.day))

    if form.validate_on_submit():
        year = int(form.year.data)
        month = int(form.month.data)
        day = int(form.day.data)

        age = calculate_age(date(year,month,day))
        
        session['age'] = age
        session['goal'] = form.goal.data
        session['goal_weight'] = form.goal_weight.data
        session['activity'] = form.activity.data
        session['height'] = form.height.data
        session['weight'] = form.weight.data
        session['rate'] = form.rate.data
        session['diet_type'] = form.diet_type.data
        session['budget'] = form.budget.data
        session['unit'] = form.unit.data

        return redirect("/signup")

    else:
        return render_template('goals.html', form=form)



@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup."""
   
    form = SignUpForm()
    
    if form.validate_on_submit():
        try:
            unit = session.get('unit')

            if unit == 'met':
                
                met_goal_weight = session.get('goal_weight')
                met_weight = session.get('weight')
                met_height = session.get('height')

                user = User.signup(

                email=form.email.data,
                password=form.password.data,
                name=form.name.data,
                sex=form.sex.data,
                unit=unit,

                age = session.get('age'),
                goal = session.get('goal'),
                goal_weight= met_goal_weight * 2.205,
                activity=session.get('activity'),
                height=met_height/2.54,
                weight=met_weight * 2.205,
                rate=session.get('rate'),
                diet_type=session.get('diet_type', None),
                budget=session.get('budget')
            )
            else:     
                user = User.signup(

                email=form.email.data,
                password=form.password.data,
                name=form.name.data,
                sex=form.sex.data,
                unit=unit,
                age = session.get('age'),
                goal=session.get('goal'),
                goal_weight=session.get('goal_weight'),
                activity=session.get('activity'),
                height=session.get('height'),
                weight=session.get('weight'),
                rate=session.get('rate'),
                diet_type=session.get('diet_type', None),
                budget=session.get('budget') 
            )
            db.session.commit()

            tdee = 0

            if user.sex == 'm':
                bmr = 66 + (6.2 * user.weight) + (12.7 * user.height) - (6.76 * user.age)
        
            else:
                bmr = 655 + ( 4.35 * user.weight) + ( 4.7 * user.height) - ( 4.7 * user.age)

            if user.activity == 'sedentary':
                tdee = bmr * 1.2
            if user.activity == 'light':
                tdee = bmr * 1.4
            if user.activity == 'active':
                tdee = bmr * 1.8

            if user.goal == 'maintain':
                daily_calories = tdee
    
            if user.goal == 'lose':
                if user.rate == 'slow':
                    daily_calories = tdee - 175
                if user.rate =='normal':
                    daily_calories = tdee - 300
                if user.rate =='fast':
                    daily_calories = tdee - 500   
    
            if user.goal == 'gain':
                if user.rate == 'slow':
                    daily_calories = tdee + 175
                if user.rate =='normal':
                    daily_calories = tdee + 300
                if user.rate =='fast':
                    daily_calories = tdee + 500           


            calories = Calorie(user_id = user.id, calories = int(daily_calories))
            db.session.add(calories)
            db.session.commit()
            
            del session['unit']
            del session['age']
            del session['goal']
            del session['goal_weight']
            del session['activity']
            del session['height']
            del session['weight']
            del session['rate']
            del session['diet_type']
            del session['budget']
     
        except IntegrityError:
            flash("Email associated with already existing account", 'danger')
            return render_template('index.html', form=form)

        do_login(user)

        return redirect(f"/home/{user.id}")

    else:
        return render_template('signup.html', form=form)


@app.route('/home/<int:user_id>', methods=["GET"])
def home(user_id):
    """User Home."""

    user = User.query.get_or_404(user_id)
    db_calorie = Calorie.query.get_or_404(user_id)
        
    total = 0
    
    for meal in user.meal:
        
        total = total + meal.calories

    calorie = db_calorie.calories - total

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    return render_template('home.html', user=user, calorie=calorie)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    user = User.query.get_or_404(session[CURR_USER_KEY])

    if session[CURR_USER_KEY] == user.id:
        do_logout()
        flash(f"{user.name} is logged out.", "success")                            
        return redirect("/")
    
    flash("Invalid logout attempt!", "danger")


@app.route('/user_details/<int:user_id>', methods=["GET"])
def settings(user_id):
    """User Settings."""

    user = User.query.get_or_404(user_id)

    total = 0

    for meal in user.meal:
        
        total = total + float(meal.price)

    remain = user.budget - total 

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    return render_template('user_details.html', user=user, remain=remain)


@app.route('/edit/<int:user_id>', methods=["GET", "POST"])
def edit(user_id):
    """User Edit."""

    form = EditUserForm()
    user = User.query.get_or_404(user_id)
    calories = Calorie.query.get_or_404(user_id)

    unit = form.unit.data

    if form.validate_on_submit():

        if g.user:        
            user.goal = form.goal.data
            user.activity = form.activity.data
            user.rate = form.rate.data
            user.diet_type = form.diet_type.data
            user.budget = form.budget.data
            user.email = form.email.data

            if unit =='met':
                user.weight = form.weight.data * 2.205
                user.goal_weight = form.goal_weight.data * 2.205
            else:    
                user.weight = form.weight.data
                user.goal_weight = form.goal_weight.data
            

            db.session.commit()

            tdee = 0


            if user.sex == 'm':
                bmr = 66 + (6.2 * user.weight) + (12.7 * user.height) - (6.76 * user.age)
        
            else:
                bmr = 655 + ( 4.35 * user.weight) + ( 4.7 * user.height) - ( 4.7 * user.age)

            if user.activity == 'sedentary':
                tdee = bmr * 1.2
            if user.activity == 'light':
                tdee = bmr * 1.4
            if user.activity == 'active':
                tdee = bmr * 1.8

            if user.goal == 'maintain':
                daily_calories = tdee
    
            if user.goal == 'lose':
                if user.rate == 'slow':
                    daily_calories = tdee - 175
                if user.rate =='normal':
                    daily_calories = tdee - 300
                if user.rate =='fast':
                    daily_calories = tdee - 500   
    
            if user.goal == 'gain':
                if user.rate == 'slow':
                    daily_calories = tdee + 175
                if user.rate =='normal':
                    daily_calories = tdee + 300
                if user.rate =='fast':
                    daily_calories = tdee + 500

            calories.calories = int(daily_calories),

            db.session.commit()

            flash(f"{user.name} profile updated!", "success")
            return redirect(f"/home/{user.id}")

        flash("Invalid attempt.", 'danger')
           
    else:
        return render_template('edit.html', form=form, user=user)


@app.route('/weight/<int:user_id>', methods=["GET", "POST"])
def edit_weight(user_id):
    """User Weight Edit."""

    form = EditUserWeightForm()
    user = User.query.get_or_404(user_id)
    calories = Calorie.query.get_or_404(user_id)
    unit = form.unit.data

    if form.validate_on_submit():

        if g.user:
            
            if unit =='met':
                user.weight = form.weight.data * 2.205
            else:    
                user.weight = form.weight.data

            db.session.commit()

            tdee = 0

            if user.sex == 'm':
                bmr = 66 + (6.2 * user.weight) + (12.7 * user.height) - (6.76 * user.age)
        
            else:
                bmr = 655 + ( 4.35 * user.weight) + ( 4.7 * user.height) - ( 4.7 * user.age)

            if user.activity == 'sedentary':
                tdee = bmr * 1.2
            if user.activity == 'light':
                tdee = bmr * 1.4
            if user.activity == 'active':
                tdee = bmr * 1.8

            if user.goal == 'maintain':
                daily_calories = tdee
    
            if user.goal == 'lose':
                if user.rate == 'slow':
                    daily_calories = tdee - 175
                if user.rate =='normal':
                    daily_calories = tdee - 300
                if user.rate =='fast':
                    daily_calories = tdee - 500   
    
            if user.goal == 'gain':
                if user.rate == 'slow':
                    daily_calories = tdee + 175
                if user.rate =='normal':
                    daily_calories = tdee + 300
                if user.rate =='fast':
                    daily_calories = tdee + 500

            calories.calories = int(daily_calories),
                       

            db.session.commit()

            flash(f"{user.name} weight updated!", "success")
            return redirect(f"/home/{user.id}")
        
        flash("Invalid attempt.", 'danger')
      
    else:
        return render_template('weight.html', form=form, user=user)



@app.route('/meal/search/<int:user_id>', methods=["GET", "POST"])
def search_meal(user_id):
    """User Meal Search."""

    form = AddMealForm()
    user = User.query.get_or_404(user_id)

    if form.validate_on_submit():
  
        if g.user:
            
            search = form.meal.data
            session['search'] = search
            return redirect(f"/meal/search/results/{user.id}")
        
        flash("Invalid attempt.", 'danger')
       
    else:

        return render_template('search_meals.html', form=form, user=user)


@app.route('/meal/search/results/<int:user_id>', methods=["GET"])
def show_search_meal(user_id):
    """Meal Search"""

    user = User.query.get_or_404(user_id)
    db_calorie = Calorie.query.get_or_404(user_id)
    
    total = 0
    
    for meal in user.meal:
        
        total = total + meal.calories

    calorie = db_calorie.calories - total 

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    search = session.get('search')

    if user.diet_type == 'gf':

        resp = requests.get(f"https://api.spoonacular.com/recipes/complexSearch?query={search}&intolerances=gluten&number=10&apiKey=54003eed12564ac69e23325328cefba2&addRecipeNutrition=true")
    
    elif user.diet_type == 'vegan':

        resp = requests.get(f"https://api.spoonacular.com/recipes/complexSearch?query={search}&diet=vegan&number=10&apiKey=54003eed12564ac69e23325328cefba2&addRecipeNutrition=true")

    elif user.diet_type == 'veg':

        resp = requests.get(f"https://api.spoonacular.com/recipes/complexSearch?query={search}&diet=vegetarian&number=10&apiKey=54003eed12564ac69e23325328cefba2&addRecipeNutrition=true")

    else: 
        resp = requests.get(f"https://api.spoonacular.com/recipes/complexSearch?query={search}&number=10&apiKey=54003eed12564ac69e23325328cefba2&addRecipeNutrition=true")

    meals = resp.json()
        
    return render_template("meal_results.html", meals=meals, user=user, calorie=calorie)   


@app.route('/meal/details/<int:meal_id>', methods=['GET'])
def show_meal_details(meal_id):
    """Show meal details."""
    
    resp_nut = requests.get(f"https://api.spoonacular.com/recipes/{meal_id}/nutritionWidget.json?apiKey=54003eed12564ac69e23325328cefba2")
    resp_title = requests.get(f"https://api.spoonacular.com/recipes/{meal_id}/summary?apiKey=54003eed12564ac69e23325328cefba2")
    resp_recipe = requests.get(f"https://api.spoonacular.com/recipes/{meal_id}/analyzedInstructions?apiKey=54003eed12564ac69e23325328cefba2")
    resp_ing = requests.get(f"https://api.spoonacular.com/recipes/{meal_id}/priceBreakdownWidget.json?apiKey=54003eed12564ac69e23325328cefba2")
    
    user = User.query.get_or_404(session[CURR_USER_KEY])

    id = meal_id
    nut_details = resp_nut.json()
    title = resp_title.json()['title']
    rec_data = resp_recipe.json()
    ing_data = resp_ing.json()

    meal_price = ing_data['totalCost']

    session['price'] = int(meal_price)/100
    session['meal_title'] = title
    session['nut_details'] = nut_details
    
    return render_template("meal_details.html", title=title, nut_details=nut_details, id=id, user=user, rec_data=rec_data,ing_data=ing_data)


@app.route('/meal/details/<int:meal_id>', methods=['POST'])
def add_meal(meal_id):
    """Handle add meal"""

    id = meal_id
    title = session.get('meal_title')
    nut_details = session.get('nut_details')
    price = session.get('price')

    cal = Calorie.query.get_or_404(session[CURR_USER_KEY])

    user = User.query.get_or_404(session[CURR_USER_KEY])

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    meal = Meal(id = id, name = title, calories = nut_details['calories'], protien = nut_details['protein'], 
                fat = nut_details['fat'], carbohydrate = nut_details['carbs'], price = price, user_id = user.id)

    db.session.add(meal)
    db.session.commit()

    return redirect("/")


@app.route('/meals/<int:user_id>', methods=['GET'])
def all_meals(user_id):
    """Show all meals"""
    
    user = User.query.get_or_404(user_id)
    db_calorie = Calorie.query.get_or_404(user_id)
    
    total = 0
    
    for meal in user.meal:
        
        total = total + meal.calories

    calorie = db_calorie.calories - total

    return render_template('meals.html', user=user, calorie=calorie)

@app.route('/meal/delete/<int:meal_id>', methods=['POST'])
def delete_meals(meal_id):
    """Delete meals"""

    user = User.query.get_or_404(session[CURR_USER_KEY])

    meal = Meal.query.get(meal_id)

    db.session.delete(meal)
    db.session.commit()

    return redirect(f'/meals/{user.id}')