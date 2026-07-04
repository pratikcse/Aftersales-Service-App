import os
from flask import Flask
from extensions import db, login_manager
from models import User


def create_app():
    app = Flask(__name__)
    basedir = os.path.abspath(os.path.dirname(__file__))

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "aftersales.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = os.path.join(basedir, "static", "uploads")
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from blueprints.auth import auth_bp
    from blueprints.main import main_bp
    from blueprints.quotations import quotations_bp
    from blueprints.workorders import workorders_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(quotations_bp)
    app.register_blueprint(workorders_bp)

    @app.context_processor
    def inject_company():
        from models import CompanySettings
        s = db.session.get(CompanySettings, 1)
        return {"company": s}

    with app.app_context():
        db.create_all()
        from migrations import run_migrations
        run_migrations()
        _ensure_settings_row()

    return app


def _ensure_settings_row():
    from models import CompanySettings
    if db.session.get(CompanySettings, 1) is None:
        db.session.add(CompanySettings(id=1))
        db.session.commit()


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
