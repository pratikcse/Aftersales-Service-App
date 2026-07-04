from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db
from models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            next_url = request.args.get("next")
            return redirect(next_url or url_for("main.dashboard"))
        flash("Invalid email or password.", "danger")

    no_users_yet = User.query.count() == 0
    return render_template("login.html", no_users_yet=no_users_yet)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth_bp.route("/setup", methods=["GET", "POST"])
def setup():
    """First-run only: create the initial admin account when no users exist."""
    if User.query.count() > 0:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        user = User(
            name=request.form.get("name", "").strip(),
            email=request.form.get("email", "").strip().lower(),
            initials=request.form.get("initials", "").strip().upper(),
            designation=request.form.get("designation", "").strip(),
            handphone=request.form.get("handphone", "").strip(),
            is_admin=True,
        )
        user.set_password(request.form.get("password", ""))
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash("Admin account created. Welcome!", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("setup.html")


@auth_bp.route("/users", methods=["GET", "POST"])
@login_required
def users():
    if not current_user.is_admin:
        flash("Only admins can manage users.", "danger")
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        if User.query.filter_by(email=email).first():
            flash("A user with that email already exists.", "danger")
        else:
            user = User(
                name=request.form.get("name", "").strip(),
                email=email,
                initials=request.form.get("initials", "").strip().upper(),
                designation=request.form.get("designation", "").strip(),
                handphone=request.form.get("handphone", "").strip(),
                is_admin=bool(request.form.get("is_admin")),
            )
            user.set_password(request.form.get("password", "changeme123"))
            db.session.add(user)
            db.session.commit()
            flash(f"User {user.name} created.", "success")
        return redirect(url_for("auth.users"))

    all_users = User.query.order_by(User.name).all()
    return render_template("users.html", users=all_users)


@auth_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash("Only admins can manage users.", "danger")
        return redirect(url_for("main.dashboard"))
    if user_id == current_user.id:
        flash("You can't delete your own account while logged in.", "danger")
        return redirect(url_for("auth.users"))
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("User removed.", "success")
    return redirect(url_for("auth.users"))
