import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Создание приложения
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-for-yayco-market")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Конфигурация базы данных
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///yayco_market.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Настройка загрузки файлов
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB per file
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Создание папки для загрузок
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Инициализация расширений
db.init_app(app)

with app.app_context():
    # Импортируем модели и маршруты
    import models
    import routes
    
    # Создание таблиц
    db.create_all()
