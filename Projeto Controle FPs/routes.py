import os
import datetime as dt
import uuid
from flask import Blueprint, current_app, render_template, request, redirect, url_for
from pymongo import MongoClient

pages = Blueprint("habits",__name__,template_folder="templates",static_folder="estatico")


@pages.context_processor
def add_defs():
    def date_range(start: dt.datetime):
        dates=[start + dt.timedelta(days=diff) for diff in range(-3, 4)]
        return dates
    return {"date_range": date_range}

def date_midn(date: dt.datetime):
    nova=date.replace(hour=0,minute=0,second=0,microsecond=0)
    return nova

@pages.route("/")
def habitos():
    
    date_str=request.args.get("date")
    if date_str:
        selected_date=dt.datetime.fromisoformat(date_str)
    else:
        selected_date=date_midn(dt.datetime.today())
    habits_on_date=[habit 
                    for habit in current_app.db.posts.find({"Ad_data":{"$lte":selected_date}})]
    completions=[habit['habit'] 
                    for habit in current_app.db.completions.find({"date":str(selected_date)})]
    return render_template("habits.html",
                            title="Habit Tracker",
                            habits=habits_on_date,
                            selected_date=selected_date,
                            completions=completions)

@pages.route("/add", methods=["GET","POST"])
def novohabito():
    if request.method == "POST":
        habito=request.form.get("habit")
        date=date_midn(dt.datetime.today())
        current_app.db.posts.insert_one({"_id":uuid.uuid4().hex,
                                    "Nome":habito,
                                    "Ad_data":date,
                                    "Ativo":True})
    date=date_midn(dt.datetime.today())
    return render_template("add.html",
                            title="Habit Tracker - Add",
                            selected_date=date)

@pages.route("/complete", methods=["POST"])
def complete():
    if request.method == "POST":
        date=request.form.get("date")
        habit=request.form.get("habitId")
        current_app.db.completions.insert_one({"date":date,
                                                "habit":habit})
        
    return redirect(url_for('habits.habitos',date=date))

@pages.route("/drop", methods=["POST","GET"])
def deletahabito():
    date=date_midn(dt.datetime.today())
    habits=[habit for habit in current_app.db.posts.find({"Ativo":True})]
    todel = [habit['habit'] for habit in current_app.db.dropped.find({})]
    if request.method == "POST":
        drop=request.form.get("habitId")
        situation=request.form.get("confirmation")
        if situation == "U":
            current_app.db.dropped.insert_one({'habit':drop})
            todel = [habit['habit'] for habit in current_app.db.dropped.find({})]
        elif situation =="S":
            current_app.db.dropped.delete_one({'habit':drop})
            todel = [habit['habit'] for habit in current_app.db.dropped.find({})]
        else:
            todel = [habit['habit'] for habit in current_app.db.dropped.find({})]
            for deletar in todel:
                current_app.db.posts.update_one({"_id":deletar},{"$set":{"Ativo":False}})
            current_app.db.dropped.delete_many({})
            habits=[habit for habit in current_app.db.posts.find({"Ativo":True})]
            
    return render_template("drop.html",
                            title="Habit Tracker - Drop",
                            habits=habits,
                            dropped=todel,
                            selected_date=date)