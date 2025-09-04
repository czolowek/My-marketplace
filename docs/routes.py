import os
from flask import render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from app import app, db
from models import Product, ProductImage
import uuid

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ADMIN_PASSWORD = "3252"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_next_image_number():
    """Получает следующий доступный номер изображения"""
    try:
        images_dir = app.config['IMAGES_FOLDER']
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)
        
        # Находим все файлы images*.* 
        existing_numbers = []
        for filename in os.listdir(images_dir):
            if filename.startswith('images') and '.' in filename:
                try:
                    number = int(filename.split('.')[0].replace('images', ''))
                    existing_numbers.append(number)
                except ValueError:
                    continue
        
        # Возвращаем следующий доступный номер
        if not existing_numbers:
            return 1
        return max(existing_numbers) + 1
    except Exception:
        return 1

def get_available_images():
    """Получает список доступных изображений из папки docs/images"""
    try:
        images_dir = app.config['IMAGES_FOLDER']
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)
        
        # Находим все файлы images1.*, images2.*, images3.*...
        available_images = []
        for filename in os.listdir(images_dir):
            if filename.startswith('images') and '.' in filename:
                # Извлекаем номер из имени файла (images1.jpg -> 1)
                try:
                    number = int(filename.split('.')[0].replace('images', ''))
                    available_images.append((number, filename))
                except ValueError:
                    continue
        
        # Сортируем по номеру
        available_images.sort(key=lambda x: x[0])
        return [filename for _, filename in available_images]
    except Exception:
        return []

@app.route('/')
def index():
    products = Product.query.order_by(Product.created_at.desc()).all()
    
    # Для каждого товара без изображений в БД, ищем изображения в docs/images
    for product in products:
        if not product.images:
            available_images = get_available_images()
            # Связываем изображения с товаром по порядку
            images_to_assign = available_images[:5]  # Максимум 5 изображений на товар
            
            for image_filename in images_to_assign:
                # Проверяем, что изображение еще не связано с каким-то товаром
                existing_image = ProductImage.query.filter_by(filename=image_filename).first()
                if not existing_image:
                    product_image = ProductImage()
                    product_image.filename = image_filename
                    product_image.product_id = product.id
                    db.session.add(product_image)
            
            db.session.commit()
    
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
                    
                # Получаем расширение файла
                file_extension = file.filename.rsplit('.', 1)[1].lower()
                
                # Получаем следующий номер изображения
                image_number = get_next_image_number()
                image_filename = f"images{image_number}.{file_extension}"
                filepath = os.path.join(app.config['IMAGES_FOLDER'], image_filename)
                file.save(filepath)
                
                # Создаем запись изображения
                product_image = ProductImage()
                product_image.filename = image_filename
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
                filepath = os.path.join(app.config['IMAGES_FOLDER'], image.filename)
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
                    
                # Получаем расширение файла  
                file_extension = file.filename.rsplit('.', 1)[1].lower()
                
                # Получаем следующий номер изображения
                image_number = get_next_image_number()
                image_filename = f"images{image_number}.{file_extension}"
                filepath = os.path.join(app.config['IMAGES_FOLDER'], image_filename)
                file.save(filepath)
                
                # Создаем запись изображения
                product_image = ProductImage()
                product_image.filename = image_filename
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
        filepath = os.path.join(app.config['IMAGES_FOLDER'], image.filename)
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

@app.route('/upload_temp_image', methods=['POST'])
def upload_temp_image():
    """Загружает изображение сразу при выборе файла"""
    if 'image' not in request.files:
        return jsonify({'error': 'Нет файла'}), 400
    
    file = request.files['image']
    if not file.filename or file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Неверный формат файла'}), 400
    
    # Получаем расширение файла
    file_extension = file.filename.rsplit('.', 1)[1].lower()
    
    # Получаем следующий номер изображения
    image_number = get_next_image_number()
    image_filename = f"images{image_number}.{file_extension}"
    filepath = os.path.join(app.config['IMAGES_FOLDER'], image_filename)
    
    file.save(filepath)
    
    return jsonify({
        'success': True,
        'filename': image_filename,
        'url': f'/docs/images/{image_filename}'
    })

@app.route('/docs/images/<filename>')
def docs_images_files(filename):
    """Статическое обслуживание файлов из папки docs/images"""
    return send_from_directory(app.config['IMAGES_FOLDER'], filename)

@app.route('/docs/<filename>')
def docs_files(filename):
    """Статическое обслуживание файлов из папки docs (для обратной совместимости)"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
