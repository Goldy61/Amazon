// 🔥 CRAZY E-COMMERCE PLATFORM JAVASCRIPT 🔥

document.addEventListener('DOMContentLoaded', function() {
    // Initialize theme
    initializeTheme();
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Fix dropdown positioning issues
    const dropdowns = document.querySelectorAll('.dropdown-toggle');
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('click', function(e) {
            // Ensure dropdown doesn't get cut off by viewport
            const dropdownMenu = this.nextElementSibling;
            if (dropdownMenu && dropdownMenu.classList.contains('dropdown-menu')) {
                // Add a small delay to let Bootstrap handle the positioning first
                setTimeout(() => {
                    const rect = dropdownMenu.getBoundingClientRect();
                    const viewportWidth = window.innerWidth;
                    
                    // If dropdown goes off-screen, adjust position
                    if (rect.right > viewportWidth) {
                        dropdownMenu.style.left = 'auto';
                        dropdownMenu.style.right = '0';
                    }
                }, 10);
            }
        });
    });

    // Auto-hide alerts after 5 seconds with animation
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            alert.style.animation = 'slideOutRight 0.5s ease-in-out';
            setTimeout(() => {
                var bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 500);
        });
    }, 5000);

    // Add sparkle effect to important elements
    addSparkleEffect();
    
    // Add floating animation to cards
    addFloatingAnimation();
    
    // Initialize crazy animations
    initializeCrazyAnimations();

    // Image preview for file uploads with animation
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    imageInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    let preview = document.getElementById('imagePreview');
                    if (!preview) {
                        preview = document.createElement('img');
                        preview.id = 'imagePreview';
                        preview.className = 'image-preview img-thumbnail mt-2';
                        preview.style.animation = 'bounceIn 0.6s ease-out';
                        preview.style.maxWidth = '200px';
                        preview.style.maxHeight = '200px';
                        preview.style.objectFit = 'cover';
                        input.parentNode.appendChild(preview);
                    }
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });
    });

    // Handle image loading errors globally
    document.addEventListener('error', function(e) {
        if (e.target.tagName === 'IMG') {
            console.log('Image failed to load:', e.target.src);
            
            // Set a placeholder image for broken images
            if (!e.target.dataset.errorHandled) {
                e.target.dataset.errorHandled = 'true';
                
                // Try placeholder image first
                if (e.target.src.indexOf('placeholder.jpg') === -1) {
                    e.target.src = '/static/images/placeholder.jpg';
                } else {
                    // If placeholder also fails, show a CSS-based placeholder
                    e.target.style.display = 'none';
                    
                    const placeholder = document.createElement('div');
                    placeholder.className = 'image-placeholder';
                    placeholder.style.cssText = `
                        width: ${e.target.width || 200}px;
                        height: ${e.target.height || 200}px;
                        background: var(--border-color);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: var(--text-color);
                        font-size: 14px;
                        border-radius: 10px;
                        opacity: 0.6;
                    `;
                    placeholder.textContent = '🖼️ Image not available';
                    
                    e.target.parentNode.insertBefore(placeholder, e.target);
                }
            }
        }
    }, true);

    // Enhanced quantity controls for cart
    const quantityControls = document.querySelectorAll('.quantity-control');
    quantityControls.forEach(function(control) {
        const minusBtn = control.querySelector('.quantity-minus');
        const plusBtn = control.querySelector('.quantity-plus');
        const input = control.querySelector('.quantity-input');

        if (minusBtn && plusBtn && input) {
            minusBtn.addEventListener('click', function() {
                let value = parseInt(input.value);
                if (value > 1) {
                    input.value = value - 1;
                    animateButton(this);
                    updateCartItem(input);
                }
            });

            plusBtn.addEventListener('click', function() {
                let value = parseInt(input.value);
                let max = parseInt(input.getAttribute('max')) || 999;
                if (value < max) {
                    input.value = value + 1;
                    animateButton(this);
                    updateCartItem(input);
                }
            });

            input.addEventListener('change', function() {
                updateCartItem(input);
            });
        }
    });

    // Enhanced search functionality
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const searchInput = document.getElementById('searchInput');
            if (searchInput && searchInput.value.trim() === '') {
                e.preventDefault();
                searchInput.focus();
                searchInput.style.animation = 'shake 0.5s ease-in-out';
            }
        });
    }

    // Enhanced price range filter
    const priceRange = document.getElementById('priceRange');
    if (priceRange) {
        priceRange.addEventListener('input', function() {
            const priceDisplay = document.getElementById('priceDisplay');
            if (priceDisplay) {
                priceDisplay.textContent = '₹' + this.value;
                priceDisplay.style.animation = 'pulse 0.3s ease-in-out';
            }
        });
    }

    // Enhanced confirmation dialogs
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('🗑️ Are you sure you want to delete this item? This action cannot be undone!')) {
                e.preventDefault();
            } else {
                this.innerHTML = '<span class="loading"></span> Deleting...';
            }
        });
    });

    // Enhanced form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                // Add shake animation to invalid fields
                const invalidFields = form.querySelectorAll(':invalid');
                invalidFields.forEach(field => {
                    field.style.animation = 'shake 0.5s ease-in-out';
                });
            }
            form.classList.add('was-validated');
        });
    });
});

// 🌙 Dark Mode Functionality - Black & White Theme
function toggleTheme() {
    const body = document.body;
    const themeIcon = document.getElementById('themeIcon');
    const themeText = document.getElementById('themeText');
    const themeToggle = document.getElementById('themeToggle');
    
    const currentTheme = body.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    // Add smooth transition animation
    body.style.transition = 'background-color 0.5s ease, color 0.5s ease';
    
    body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Update button with animation
    if (newTheme === 'dark') {
        themeIcon.className = 'fas fa-sun';
        if (themeText) themeText.textContent = 'Light';
        if (themeToggle) {
            themeToggle.style.animation = 'fadeIn 0.5s ease-in-out';
            themeToggle.title = 'Switch to Light Mode';
        }
        
        // Show notification
        showThemeNotification('🌙 Dark Mode Activated - Black & White Theme');
    } else {
        themeIcon.className = 'fas fa-moon';
        if (themeText) themeText.textContent = 'Dark';
        if (themeToggle) {
            themeToggle.style.animation = 'fadeIn 0.5s ease-in-out';
            themeToggle.title = 'Switch to Dark Mode';
        }
        
        // Show notification
        showThemeNotification('☀️ Light Mode Activated - Brown & Cream Theme');
    }
    
    // Reset animation
    setTimeout(() => {
        if (themeToggle) themeToggle.style.animation = '';
    }, 500);
}

function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    const body = document.body;
    const themeIcon = document.getElementById('themeIcon');
    const themeText = document.getElementById('themeText');
    const themeToggle = document.getElementById('themeToggle');
    
    body.setAttribute('data-theme', savedTheme);
    
    if (savedTheme === 'dark') {
        if (themeIcon) themeIcon.className = 'fas fa-sun';
        if (themeText) themeText.textContent = 'Light';
        if (themeToggle) themeToggle.title = 'Switch to Light Mode';
    } else {
        if (themeIcon) themeIcon.className = 'fas fa-moon';
        if (themeText) themeText.textContent = 'Dark';
        if (themeToggle) themeToggle.title = 'Switch to Dark Mode';
    }
}

// Show theme change notification
function showThemeNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'theme-notification';
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        background: var(--card-bg);
        color: var(--text-color);
        padding: 1rem 1.5rem;
        border-radius: 12px;
        box-shadow: 0 8px 24px var(--shadow-color);
        z-index: 9999;
        animation: slideInRight 0.5s ease-out;
        border: 2px solid var(--border-color);
        font-weight: 600;
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.5s ease-in';
        setTimeout(() => {
            notification.remove();
        }, 500);
    }, 3000);
}

// ✨ Crazy Animation Functions
function addSparkleEffect() {
    const importantElements = document.querySelectorAll('.btn-primary, .navbar-brand, .card-title');
    importantElements.forEach(element => {
        if (Math.random() > 0.7) { // Random sparkle
            element.classList.add('sparkle');
        }
    });
}

function addFloatingAnimation() {
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        if (index % 3 === 0) { // Every third card floats
            card.classList.add('float');
            card.style.animationDelay = `${index * 0.2}s`;
        }
    });
}

function initializeCrazyAnimations() {
    // Add neon glow to random elements
    const glowElements = document.querySelectorAll('h1, h2, .navbar-brand');
    glowElements.forEach(element => {
        if (Math.random() > 0.5) {
            element.classList.add('neon-glow');
        }
    });
    
    // Add entrance animations to cards
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'slideInUp 0.6s ease-out';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.card, .product-card').forEach(card => {
        observer.observe(card);
    });
}

function animateButton(button) {
    button.style.transform = 'scale(0.95)';
    button.style.animation = 'pulse 0.3s ease-in-out';
    setTimeout(() => {
        button.style.transform = '';
        button.style.animation = '';
    }, 300);
}

// Update cart item quantity with animation
function updateCartItem(input) {
    const cartId = input.getAttribute('data-cart-id');
    const quantity = input.value;
    
    if (cartId && quantity) {
        // Add loading animation
        input.style.background = 'linear-gradient(45deg, #667eea, #764ba2)';
        input.style.color = 'white';
        
        // Create form and submit
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/update_cart';
        form.style.display = 'none';
        
        const cartIdInput = document.createElement('input');
        cartIdInput.type = 'hidden';
        cartIdInput.name = 'cart_id';
        cartIdInput.value = cartId;
        
        const quantityInput = document.createElement('input');
        quantityInput.type = 'hidden';
        quantityInput.name = 'quantity';
        quantityInput.value = quantity;
        
        form.appendChild(cartIdInput);
        form.appendChild(quantityInput);
        document.body.appendChild(form);
        form.submit();
    }
}

// Enhanced add to cart with AJAX and animations
function addToCart(productId, quantity = 1) {
    console.log('addToCart called with productId:', productId, 'quantity:', quantity);
    
    const formData = new FormData();
    formData.append('product_id', productId);
    formData.append('quantity', quantity);
    
    // Show loading animation
    const addButton = event ? event.target.closest('button') : null;
    const originalText = addButton ? addButton.innerHTML : '';
    if (addButton) {
        addButton.innerHTML = '<span class="loading"></span> Adding...';
        addButton.disabled = true;
    }
    
    fetch('/add_to_cart', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        console.log('Response status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Response data:', data);
        if (data.success) {
            showAlert('🛒 Item added to cart!', 'success');
            updateCartCount();
            // Success animation
            if (addButton) {
                addButton.style.background = 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)';
                addButton.innerHTML = '✅ Added!';
            }
        } else {
            showAlert('❌ ' + (data.message || 'Error adding item to cart'), 'error');
            if (addButton) {
                addButton.innerHTML = originalText;
            }
        }
        
        setTimeout(() => {
            if (addButton) {
                addButton.innerHTML = originalText;
                addButton.disabled = false;
                addButton.style.background = '';
            }
        }, 2000);
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('❌ Error adding item to cart', 'error');
        if (addButton) {
            addButton.innerHTML = originalText;
            addButton.disabled = false;
        }
    });
}

// Quick Add to Cart function for product listings
function addToCartQuick(productId, quantity = 1) {
    console.log('addToCartQuick called with productId:', productId, 'quantity:', quantity);
    
    // Prevent event bubbling
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    
    // Call the main addToCart function
    addToCart(productId, quantity);
}

// Buy Now function for quick purchase
function buyNow(productId, quantity = 1) {
    console.log('buyNow called with productId:', productId, 'quantity:', quantity);
    
    // Prevent event bubbling
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    
    // Find the button that was clicked
    const buyButton = event ? event.target.closest('button') : null;
    let originalText = '';
    
    if (buyButton) {
        originalText = buyButton.innerHTML;
        buyButton.innerHTML = '<span class="loading"></span> Processing...';
        buyButton.disabled = true;
        buyButton.style.background = 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)';
    }
    
    // Create form for buy now
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/buy_now';
    form.style.display = 'none';
    
    const productIdInput = document.createElement('input');
    productIdInput.type = 'hidden';
    productIdInput.name = 'product_id';
    productIdInput.value = productId;
    
    const quantityInput = document.createElement('input');
    quantityInput.type = 'hidden';
    quantityInput.name = 'quantity';
    quantityInput.value = quantity;
    
    form.appendChild(productIdInput);
    form.appendChild(quantityInput);
    document.body.appendChild(form);
    
    // Submit after short delay for animation
    setTimeout(() => {
        console.log('Submitting buy now form');
        form.submit();
    }, 500);
}

// Buy Now from product detail page
function buyNowFromDetail() {
    // Prevent event bubbling
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    
    const quantitySelect = document.getElementById('quantity');
    const quantity = quantitySelect ? quantitySelect.value : 1;
    const productIdInput = document.querySelector('input[name="product_id"]');
    
    if (!productIdInput) {
        showAlert('❌ Product not found', 'error');
        return;
    }
    
    const productId = productIdInput.value;
    
    // Create form for buy now
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/buy_now';
    form.style.display = 'none';
    
    const productIdFormInput = document.createElement('input');
    productIdFormInput.type = 'hidden';
    productIdFormInput.name = 'product_id';
    productIdFormInput.value = productId;
    
    const quantityFormInput = document.createElement('input');
    quantityFormInput.type = 'hidden';
    quantityFormInput.name = 'quantity';
    quantityFormInput.value = quantity;
    
    form.appendChild(productIdFormInput);
    form.appendChild(quantityFormInput);
    document.body.appendChild(form);
    
    // Show loading state
    const buyButton = event ? event.target : null;
    if (buyButton) {
        buyButton.innerHTML = '<span class="loading"></span> Processing...';
        buyButton.disabled = true;
    }
    
    form.submit();
}

// Enhanced alert messages with animations
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    alertDiv.style.animation = 'slideInRight 0.5s ease-out';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-hide after 3 seconds with animation
        setTimeout(() => {
            alertDiv.style.animation = 'slideOutRight 0.5s ease-in-out';
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alertDiv);
                bsAlert.close();
            }, 500);
        }, 3000);
    }
}

// Update cart count with animation
function updateCartCount() {
    fetch('/api/cart_count')
    .then(response => response.json())
    .then(data => {
        const cartBadge = document.getElementById('cartCount');
        if (cartBadge) {
            cartBadge.textContent = data.count;
            cartBadge.style.display = data.count > 0 ? 'inline' : 'none';
            cartBadge.style.animation = 'bounce 0.5s ease-in-out';
        }
    })
    .catch(error => console.error('Error updating cart count:', error));
}

// Enhanced format currency with animation
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(amount);
}

// Debounce function for search with enhanced UX
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Enhanced live search functionality
const searchInput = document.getElementById('liveSearch');
if (searchInput) {
    const debouncedSearch = debounce(function(query) {
        if (query.length >= 3) {
            searchInput.style.background = 'linear-gradient(45deg, #667eea, #764ba2)';
            searchInput.style.color = 'white';
            
            fetch(`/api/search?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                displaySearchResults(data.results);
                searchInput.style.background = '';
                searchInput.style.color = '';
            })
            .catch(error => {
                console.error('Search error:', error);
                searchInput.style.background = '';
                searchInput.style.color = '';
            });
        }
    }, 300);
    
    searchInput.addEventListener('input', function() {
        debouncedSearch(this.value);
    });
}

// Enhanced display search results with animations
function displaySearchResults(results) {
    const resultsContainer = document.getElementById('searchResults');
    if (!resultsContainer) return;
    
    if (results.length === 0) {
        resultsContainer.innerHTML = '<p class="text-muted">🔍 No results found</p>';
        return;
    }
    
    const html = results.map((product, index) => `
        <div class="search-result-item" style="animation: slideInLeft 0.3s ease-out ${index * 0.1}s both;">
            <a href="/product/${product.id}" class="d-flex align-items-center text-decoration-none">
                <img src="${product.image_url || '/static/images/placeholder.jpg'}" 
                     alt="${product.name}" class="me-3" style="width: 50px; height: 50px; object-fit: cover; border-radius: 10px;">
                <div>
                    <h6 class="mb-0">${product.name}</h6>
                    <small class="text-muted">${formatCurrency(product.price)}</small>
                </div>
            </a>
        </div>
    `).join('');
    
    resultsContainer.innerHTML = html;
}

// Add CSS animations dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInUp {
        0% { transform: translateY(30px); opacity: 0; }
        100% { transform: translateY(0); opacity: 1; }
    }
    
    @keyframes slideInRight {
        0% { transform: translateX(100px); opacity: 0; }
        100% { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        0% { transform: translateX(0); opacity: 1; }
        100% { transform: translateX(100px); opacity: 0; }
    }
    
    @keyframes slideInLeft {
        0% { transform: translateX(-30px); opacity: 0; }
        100% { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
`;
document.head.appendChild(style);

// Initialize on page load with welcome animation
document.addEventListener('DOMContentLoaded', function() {
    updateCartCount();
    
    // Welcome animation
    setTimeout(() => {
        const welcomeElements = document.querySelectorAll('h1, .hero-section p, .navbar-brand');
        welcomeElements.forEach((element, index) => {
            element.style.animation = `bounceIn 0.6s ease-out ${index * 0.2}s both`;
        });
    }, 100);
    
    // Add click event listeners to buttons for debugging
    document.addEventListener('click', function(e) {
        if (e.target.closest('button[onclick*="addToCartQuick"]')) {
            console.log('Add to cart button clicked');
        }
        if (e.target.closest('button[onclick*="buyNow"]')) {
            console.log('Buy now button clicked');
        }
    });
});

