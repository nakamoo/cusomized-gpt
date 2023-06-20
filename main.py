from json import JSONDecodeError
from multiprocessing import Process
import os

from google.oauth2 import id_token
from google.auth.transport import requests

from flask import render_template, request, jsonify, redirect, url_for, session

from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)

import crawler
from app import app, login_manager
from db import ModelStatus, db, User, EmbeddedIndex, Model
from job import create_model
import llm


# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/")
@app.route("/index")
def index():
    if current_user.is_authenticated:
        message = "My Page"
        link = "mypage"
    else:
        message = "Sign in/Login with Google"
        link = "login"
    return render_template("index.html", message=message, link=link)


@app.route("/login")
def login():
    if current_user.is_authenticated:
        message = "My Page"
        link = "mypage"
    else:
        message = "Sign in/Login with Google"
        link = "login"
    return render_template("login.html", message=message, link=link)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/login/authorized", methods=["POST"])
def authorize():
    token = request.form["credential"]
    idinfo = id_token.verify_oauth2_token(
        token, requests.Request(), os.environ.get("GOOGLE_CLIENT_ID")
    )
    user = load_user(idinfo["sub"])
    if user is None:
        pic_url = idinfo["picture"] if "picture" in idinfo else None
        user = User(idinfo["sub"], idinfo["name"], idinfo["email"], pic_url)
        db.session.add(user)
        db.session.commit()
    login_user(user)
    return redirect(url_for("mypage"))


@app.route("/mypage")
@login_required
def mypage():
    message = "My Page"
    link = "mypage"

    models = Model.query.filter(
        Model.user_id == current_user.id, Model.status != ModelStatus.FAILURE
    ).all()

    return render_template(
        "mypage.html",
        name=current_user.name,
        email=current_user.email,
        message=message,
        link=link,
        models=models,
        ModelStatus=ModelStatus,
    )


@app.route("/crawl", methods=["POST"])
@login_required
def crawl():
    data = request.get_json()
    # print(data)
    url = data["url"]
    try:
        urls, message = crawler.crawl(url)
        # urls = ["https://www.google.com", "https://www.yahoo.co.jp"]
        return jsonify({"urls": urls, "message": message}), 200
    except JSONDecodeError:
        return "入力が正しいURLではありません。", 500
    except Exception:
        return "エラーが発生しました。再度お試しください。", 500


@app.route("/index", methods=["POST"])
@login_required
def model_post():
    data = request.get_json()
    urls = data["urls"]
    model_name = data["model_name"]

    p = Process(target=create_model, args=(urls, current_user.id, model_name))
    p.start()

    return "", 200


@app.route("/model/<model_id>")
def model_chat(model_id):
    # TODO: ここでmodel_idを埋め込んでpageを返す
    model = Model.query.filter(
        Model.id == model_id, Model.status == ModelStatus.SUCCESS
    ).first()
    if model is None:
        return render_template("404.html"), 404

    # Clear chat history in session
    session.pop("chat_history", None)

    # TODO: assume that there is only one index for each model
    embedded_index = EmbeddedIndex.query.filter_by(id=model_id).first()

    return render_template(
        "model.html",
        index_id=embedded_index.id,
        model_name=model.name,
    )


@app.route("/query", methods=["POST"])
def query():
    data = request.get_json()
    print(data)
    query = data["query"]
    index_id = data["index_id"]

    chat_history = session.get("chat_history", [])
    print(chat_history)

    chat_engine = llm.get_chat_engine(index_id, chat_history)
    answer = chat_engine.chat(query).response.strip()
    print(answer)

    session["chat_history"] = chat_engine._chat_history
    return {"answer": answer}, 200


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
