from .auth import auth_bp
from .siswa import siswa_bp
from .guru import guru_bp
from .token import token_bp
from .api_absensi import api_absensi_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(guru_bp)
    app.register_blueprint(siswa_bp)
    app.register_blueprint(token_bp)
    app.register_blueprint(api_absensi_bp)
