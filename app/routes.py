from app import app
from flask import render_template, request, redirect, url_for, session, g, flash
from werkzeug.urls import url_parse
from app.forms import LoginForm, RegistrationForm, QuestionForm
from app.models import User, TopikQuestions, Questions
from app import db


@app.before_request
def before_request():
    g.user = None

    if "user_id" in session:
        user = User.query.filter_by(id=session["user_id"]).first()
        g.user = user


@app.route("/")
def home():
    return render_template("index.html", title="Home")


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            return redirect(url_for("login"))
        session["user_id"] = user.id
        session["marks"] = 0
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("home")
        return redirect(next_page)
        return redirect(url_for("home"))
    if g.user:
        return redirect(url_for("home"))
    return render_template("login.html", form=form, title="Login")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.password.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        session["user_id"] = user.id
        session["marks"] = 0
        return redirect(url_for("home"))
    if g.user:
        return redirect(url_for("home"))
    return render_template("register.html", title="Register", form=form)


@app.route("/question/<int:id>", methods=["GET", "POST"])
def question(id):
    if not g.user:
        return redirect(url_for("login"))

    current_id = session.get("current_id", 0)

    t = TopikQuestions.query.filter(TopikQuestions.t_id == id).first()
    print(t)

    q = (
        Questions.query.join(TopikQuestions, Questions.t_id == TopikQuestions.t_id)
        .filter_by(t_id=id)
        .order_by(Questions.q_id)
        .all()
    )
    # for question in q:
    #     print(question.ques)  # 각 질문의 내용을 출력
    print(f"Query result: {q}")
    if not q:
        return redirect(url_for("score"))

    current_ques = q[current_id]

    forms = []
    for question in q:
        # 각 질문의 선택지를 설정
        form = QuestionForm()
        form.options.choices = [
            (question.a, question.a),
            (question.b, question.b),
            (question.c, question.c),
            (question.d, question.d),
        ]
        forms.append((form, question))

    if request.method == "POST":
        option = request.form["options"]
        if option == current_ques.ans:
            session["marks"] = session.get("marks", 0) + 10

        # index update into next question
        if current_id + 1 < len(q):
            session["current_id"] = current_id + 1
            return redirect(url_for("question", id=id + 1))
            # return redirect(url_for("question", id=(id + 1)))
        else:
            return redirect(url_for("score"))

    return render_template(
        "question.html",
        form=form,
        topik=t,
        questions=q,
        title=f"Question {current_id + 1} of Topik {id}",
        # title="Question {}".format(id),
    )


@app.route("/score")
def score():
    if not g.user:
        return redirect(url_for("login"))
    g.user.marks = session["marks"]
    db.session.commit()
    return render_template("score.html", title="Final Score")


@app.route("/logout")
def logout():
    if not g.user:
        return redirect(url_for("login"))
    session.pop("user_id", None)
    session.pop("marks", None)
    return redirect(url_for("home"))
