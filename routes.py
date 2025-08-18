import os
from flask import render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from app import app, db
from models import Product, ProductImage
import uuid

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ADMIN_PASSWORD = "3252"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('general.html', products=products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        # Проверка пароля
        password = request.form.get('password')
        if password != ADMIN_PASSWORD:
            flash('Неверный пароль!', 'error')
            return render_template('product.html')
        
        # Получение данных формы
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')
        
        if not all([title, description, price]):
            flash('Все поля обязательны для заполнения!', 'error')
            return render_template('product.html')
        
        # Создание товара
        product = Product()
        product.title = title
        product.description = description
        product.price = price
        
        db.session.add(product)
        db.session.flush()  # Получаем ID товара
        
        # Обработка загрузки файлов
        uploaded_files = request.files.getlist('images')
        image_count = 0
        
        for file in uploaded_files:
            if file and file.filename and file.filename != '' and allowed_file(file.filename):
                if image_count >= 20:
                    flash('Максимум 20 изображений на товар!', 'warning')
                    break
                    
                # Генерируем уникальное имя файла
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(filepath)
                
                # Создаем запись изображения
                product_image = ProductImage()
                product_image.filename = unique_filename
                product_image.product_id = product.id
                db.session.add(product_image)
                
                image_count += 1
        
        db.session.commit()
        
        flash(f'Товар успешно добавлен с {image_count} изображениями!', 'success')
        return redirect(url_for('index'))
    
    return render_template('product.html')

@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        # Проверка пароля
        password = request.form.get('password')
        if password != ADMIN_PASSWORD:
            flash('Неверный пароль!', 'error')
            return render_template('edit_product.html', product=product)
        
        # Получение данных формы
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')
        
        if not all([title, description, price]):
            flash('Все поля обязательны для заполнения!', 'error')
            return render_template('edit_product.html', product=product)
        
        # Обновление данных товара
        product.title = title
        product.description = description
        product.price = price
        
        # Удаление выбранных изображений
        images_to_delete = request.form.getlist('delete_images')
        for image_id in images_to_delete:
            image = ProductImage.query.get(image_id)
            if image and image.product_id == product.id:
                # Удаляем файл
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
                if os.path.exists(filepath):
                    os.remove(filepath)
                db.session.delete(image)
        
        # Добавление новых изображений
        uploaded_files = request.files.getlist('new_images')
        current_image_count = len(product.images)
        new_image_count = 0
        
        for file in uploaded_files:
            if file and file.filename and file.filename != '' and allowed_file(file.filename):
                if current_image_count + new_image_count >= 20:
                    flash('Максимум 20 изображений на товар!', 'warning')
                    break
                    
                # Генерируем уникальное имя файла
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(filepath)
                
                # Создаем запись изображения
                product_image = ProductImage()
                product_image.filename = unique_filename
                product_image.product_id = product.id
                db.session.add(product_image)
                
                new_image_count += 1
        
        db.session.commit()
        
        flash('Товар успешно обновлен!', 'success')
        return redirect(url_for('product_detail', product_id=product.id))
    
    return render_template('edit_product.html', product=product)

@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    # Проверка пароля
    password = request.form.get('password')
    if password != ADMIN_PASSWORD:
        flash('Неверный пароль!', 'error')
        return redirect(url_for('product_detail', product_id=product_id))
    
    product = Product.query.get_or_404(product_id)
    
    # Удаляем все файлы изображений
    for image in product.images:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        if os.path.exists(filepath):
            os.remove(filepath)
    
    # Удаляем товар (изображения удалятся автоматически благодаря cascade)
    db.session.delete(product)
    db.session.commit()
    
    flash('Товар успешно удален!', 'success')
    return redirect(url_for('index'))

@app.route('/contact_info')
def contact_info():
    return jsonify({
        'discord': 'яйцо глеба#1234',
        'whatsapp': '+48793194133'
    })
