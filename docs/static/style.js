// Простой и чистый JavaScript
console.log('🥚 Яйцо Маркет загружен и готов к работе!');

// Gallery navigation for product cards
function nextImage(button) {
    const card = button.closest('.product-card');
    const gallery = card.querySelector('.image-gallery');
    const images = gallery.querySelectorAll('.gallery-image');
    const counter = card.querySelector('.image-counter span');
    
    let current = 0;
    images.forEach((img, index) => {
        if (img.classList.contains('active')) {
            current = index;
        }
        img.classList.remove('active');
    });
    
    const next = (current + 1) % images.length;
    images[next].classList.add('active');
    counter.textContent = next + 1;
}

function previousImage(button) {
    const card = button.closest('.product-card');
    const gallery = card.querySelector('.image-gallery');
    const images = gallery.querySelectorAll('.gallery-image');
    const counter = card.querySelector('.image-counter span');
    
    let current = 0;
    images.forEach((img, index) => {
        if (img.classList.contains('active')) {
            current = index;
        }
        img.classList.remove('active');
    });
    
    const prev = current === 0 ? images.length - 1 : current - 1;
    images[prev].classList.add('active');
    counter.textContent = prev + 1;
}

// Product detail image gallery
function changeMainImage(thumbnailItem, index) {
    const mainImage = document.getElementById('mainImage');
    const thumbnailItems = document.querySelectorAll('.thumbnail-item');
    const imageCounter = document.getElementById('currentImageIndex');
    const thumbnailImg = thumbnailItem.querySelector('.thumbnail-image');
    
    // Update main image
    mainImage.src = thumbnailImg.src;
    
    // Update active thumbnail
    thumbnailItems.forEach(item => item.classList.remove('active'));
    thumbnailItem.classList.add('active');
    
    // Update counter
    if (imageCounter) {
        imageCounter.textContent = index + 1;
    }
    
    // Smooth scroll to show active thumbnail
    thumbnailItem.scrollIntoView({
        behavior: 'smooth',
        block: 'nearest',
        inline: 'center'
    });
}

// Modal functions
function showContactModal() {
    const modal = document.getElementById('contactModal');
    modal.classList.remove('d-none');
    document.body.style.overflow = 'hidden';
}

function hideContactModal() {
    const modal = document.getElementById('contactModal');
    modal.classList.add('d-none');
    document.body.style.overflow = 'auto';
}

function showEditModal() {
    const modal = document.getElementById('editModal');
    modal.classList.remove('d-none');
    document.body.style.overflow = 'hidden';
}

function hideEditModal() {
    const modal = document.getElementById('editModal');
    modal.classList.add('d-none');
    document.body.style.overflow = 'auto';
}

function showDeleteModal() {
    const modal = document.getElementById('deleteModal');
    modal.classList.remove('d-none');
    document.body.style.overflow = 'hidden';
}

function hideDeleteModal() {
    const modal = document.getElementById('deleteModal');
    modal.classList.add('d-none');
    document.body.style.overflow = 'auto';
}

// Copy Discord ID
function copyDiscord() {
    const discordId = 'яйцо глеба#1234';
    
    if (navigator.clipboard) {
        navigator.clipboard.writeText(discordId).then(() => {
            showToast('Discord ID скопирован!', 'success');
        }).catch(() => {
            fallbackCopy(discordId);
        });
    } else {
        fallbackCopy(discordId);
    }
}

// Fallback copy for older browsers
function fallbackCopy(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.select();
    
    try {
        document.execCommand('copy');
        showToast('Discord ID скопирован!', 'success');
    } catch (err) {
        showToast('Скопируйте вручную: ' + text, 'info');
    }
    
    document.body.removeChild(textArea);
}

// Show toast notification
function showToast(message, type = 'info') {
    // Remove existing notifications
    const existing = document.querySelectorAll('.toast-notification');
    existing.forEach(toast => toast.remove());
    
    // Create new notification
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} toast-notification`;
    toast.innerHTML = `
        ${message}
        <button class="btn-close" onclick="this.parentElement.remove()">&times;</button>
    `;
    
    document.body.appendChild(toast);
    
    // Auto hide after 4 seconds
    setTimeout(() => {
        if (toast.parentElement) {
            toast.remove();
        }
    }, 4000);
}

// Preview multiple images for new product
function previewImages(input) {
    const files = Array.from(input.files);
    const preview = document.getElementById('images-preview');
    const previewGrid = document.getElementById('preview-grid');
    
    if (files.length > 20) {
        showToast('Максимум 20 изображений!', 'warning');
        input.value = '';
        return;
    }
    
    previewGrid.innerHTML = '';
    
    if (files.length > 0) {
        preview.classList.remove('d-none');
        
        // Автоматически загружаем каждое изображение
        files.forEach((file, index) => {
            if (file.type.startsWith('image/')) {
                uploadImageImmediately(file, index, previewGrid);
            }
        });
        
        const sizeMB = (files.reduce((total, file) => total + file.size, 0) / 1024 / 1024).toFixed(1);
        showToast(`${files.length} изображений загружается...`, 'info');
    } else {
        preview.classList.add('d-none');
    }
}

// Upload single image immediately
function uploadImageImmediately(file, index, previewGrid) {
    const formData = new FormData();
    formData.append('image', file);
    
    // Создаем элемент предварительного просмотра
    const previewItem = document.createElement('div');
    previewItem.className = 'preview-item uploading';
    previewItem.innerHTML = `
        <div class="upload-progress">
            <i class="fas fa-spinner fa-spin"></i>
            <div>Загрузка...</div>
        </div>
    `;
    previewGrid.appendChild(previewItem);
    
    fetch('/upload_temp_image', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            previewItem.className = 'preview-item uploaded';
            previewItem.innerHTML = `
                <img src="${data.url}" class="preview-image" alt="Загружено ${index + 1}">
                <div class="upload-success">
                    <i class="fas fa-check"></i>
                    ${data.filename}
                </div>
            `;
            showToast(`Изображение ${data.filename} загружено!`, 'success');
        } else {
            previewItem.className = 'preview-item error';
            previewItem.innerHTML = `
                <div class="upload-error">
                    <i class="fas fa-exclamation-triangle"></i>
                    <div>Ошибка: ${data.error}</div>
                </div>
            `;
            showToast(`Ошибка загрузки: ${data.error}`, 'error');
        }
    })
    .catch(error => {
        previewItem.className = 'preview-item error';
        previewItem.innerHTML = `
            <div class="upload-error">
                <i class="fas fa-exclamation-triangle"></i>
                <div>Ошибка сети</div>
            </div>
        `;
        showToast('Ошибка сети при загрузке', 'error');
    });
}

// Preview new images for edit product
function previewNewImages(input) {
    const files = Array.from(input.files);
    const preview = document.getElementById('new-images-preview');
    const previewGrid = document.getElementById('new-preview-grid');
    
    previewGrid.innerHTML = '';
    
    if (files.length > 0) {
        preview.classList.remove('d-none');
        
        files.forEach((file, index) => {
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    const previewItem = document.createElement('div');
                    previewItem.className = 'preview-item';
                    previewItem.innerHTML = `
                        <img src="${e.target.result}" class="preview-image" alt="New Preview ${index + 1}">
                    `;
                    previewGrid.appendChild(previewItem);
                };
                
                reader.readAsDataURL(file);
            }
        });
        
        showToast(`${files.length} новых изображений выбрано`, 'success');
    } else {
        preview.classList.add('d-none');
    }
}

// Remove preview image (for new products)
function removePreviewImage(button, index) {
    const input = document.getElementById('images');
    const dt = new DataTransfer();
    
    Array.from(input.files).forEach((file, i) => {
        if (i !== index) {
            dt.items.add(file);
        }
    });
    
    input.files = dt.files;
    previewImages(input);
}

// Close modal when clicking outside
document.addEventListener('click', function(e) {
    const modals = ['contactModal', 'editModal', 'deleteModal'];
    modals.forEach(modalId => {
        const modal = document.getElementById(modalId);
        if (modal && e.target === modal) {
            modal.classList.add('d-none');
            document.body.style.overflow = 'auto';
        }
    });
});

// Close modal with Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        const modals = ['contactModal', 'editModal', 'deleteModal'];
        modals.forEach(modalId => {
            const modal = document.getElementById(modalId);
            if (modal && !modal.classList.contains('d-none')) {
                modal.classList.add('d-none');
                document.body.style.overflow = 'auto';
            }
        });
    }
});

// Form validation
document.addEventListener('DOMContentLoaded', function() {
    const productForm = document.getElementById('productForm');
    const editForm = document.getElementById('editProductForm');
    
    // Validate product form
    if (productForm) {
        productForm.addEventListener('submit', function(e) {
            const password = document.getElementById('password').value;
            const title = document.getElementById('title').value.trim();
            const description = document.getElementById('description').value.trim();
            const price = document.getElementById('price').value.trim();
            
            if (!title || !description || !price || !password) {
                e.preventDefault();
                showToast('Заполните все обязательные поля', 'danger');
                return;
            }
            
            if (title.length < 3) {
                e.preventDefault();
                showToast('Название должно содержать минимум 3 символа', 'danger');
                return;
            }
            
            if (description.length < 10) {
                e.preventDefault();
                showToast('Описание должно содержать минимум 10 символов', 'danger');
                return;
            }
        });
    }
    
    // Validate edit form
    if (editForm) {
        editForm.addEventListener('submit', function(e) {
            const password = document.getElementById('password').value;
            const title = document.getElementById('title').value.trim();
            const description = document.getElementById('description').value.trim();
            const price = document.getElementById('price').value.trim();
            
            if (!title || !description || !price || !password) {
                e.preventDefault();
                showToast('Заполните все обязательные поля', 'danger');
                return;
            }
            
            if (title.length < 3) {
                e.preventDefault();
                showToast('Название должно содержать минимум 3 символа', 'danger');
                return;
            }
            
            if (description.length < 10) {
                e.preventDefault();
                showToast('Описание должно содержать минимум 10 символов', 'danger');
                return;
            }
        });
    }
});
