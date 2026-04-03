// ============================================
// SOCIAL PROOF & FOMO NOTIFICATIONS
// ============================================

class SocialProofNotifications {
    constructor() {
        this.notifications = [];
        this.currentIndex = 0;
        this.isVisible = false;
        this.container = null;
        this.init();
    }
    
    init() {
        // Create notification container
        this.container = document.createElement('div');
        this.container.className = 'social-proof-container';
        document.body.appendChild(this.container);
        
        // Load notifications
        this.loadNotifications();
        
        // Start showing notifications
        this.startNotificationCycle();
    }
    
    loadNotifications() {
        // Simulated notifications (in production, fetch from API)
        this.notifications = [
            {
                type: 'purchase',
                name: 'Rahul from Mumbai',
                product: 'Wireless Headphones',
                time: '2 minutes ago',
                icon: 'fa-shopping-cart',
                color: '#10b981'
            },
            {
                type: 'review',
                name: 'Priya from Delhi',
                product: 'Smart Watch',
                rating: 5,
                time: '5 minutes ago',
                icon: 'fa-star',
                color: '#f59e0b'
            },
            {
                type: 'stock',
                product: 'Gaming Laptop',
                stock: 3,
                time: 'Just now',
                icon: 'fa-exclamation-triangle',
                color: '#ef4444'
            },
            {
                type: 'purchase',
                name: 'Amit from Bangalore',
                product: 'Running Shoes',
                time: '8 minutes ago',
                icon: 'fa-shopping-bag',
                color: '#10b981'
            },
            {
                type: 'viewing',
                count: 12,
                product: 'iPhone 15 Pro',
                time: 'Right now',
                icon: 'fa-eye',
                color: '#3b82f6'
            }
        ];
    }
    
    startNotificationCycle() {
        // Show first notification after 3 seconds
        setTimeout(() => {
            this.showNextNotification();
        }, 3000);
    }
    
    showNextNotification() {
        if (this.isVisible) return;
        
        const notification = this.notifications[this.currentIndex];
        this.displayNotification(notification);
        
        // Move to next notification
        this.currentIndex = (this.currentIndex + 1) % this.notifications.length;
        
        // Schedule next notification
        setTimeout(() => {
            this.hideNotification();
            setTimeout(() => {
                this.showNextNotification();
            }, 5000); // Wait 5 seconds before next notification
        }, 6000); // Show for 6 seconds
    }
    
    displayNotification(data) {
        this.isVisible = true;
        
        let message = '';
        switch(data.type) {
            case 'purchase':
                message = `<strong>${data.name}</strong> just purchased <strong>${data.product}</strong>`;
                break;
            case 'review':
                message = `<strong>${data.name}</strong> gave ${data.rating} stars to <strong>${data.product}</strong>`;
                break;
            case 'stock':
                message = `Only <strong>${data.stock} left</strong> in stock for <strong>${data.product}</strong>`;
                break;
            case 'viewing':
                message = `<strong>${data.count} people</strong> are viewing <strong>${data.product}</strong>`;
                break;
        }
        
        this.container.innerHTML = `
            <div class="social-proof-notification" style="animation: slideInRight 0.5s ease;">
                <div class="notification-icon" style="background: ${data.color}">
                    <i class="fas ${data.icon}"></i>
                </div>
                <div class="notification-content">
                    <div class="notification-message">${message}</div>
                    <div class="notification-time">${data.time}</div>
                </div>
                <button class="notification-close" onclick="socialProof.hideNotification()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        this.container.classList.add('visible');
    }
    
    hideNotification() {
        this.container.classList.remove('visible');
        this.isVisible = false;
    }
}

// Initialize on page load
let socialProof;
document.addEventListener('DOMContentLoaded', () => {
    socialProof = new SocialProofNotifications();
});

// ============================================
// STOCK COUNTDOWN
// ============================================
function initStockCountdown() {
    const stockElements = document.querySelectorAll('[data-stock]');
    
    stockElements.forEach(element => {
        const stock = parseInt(element.dataset.stock);
        
        if (stock <= 10 && stock > 0) {
            const badge = document.createElement('div');
            badge.className = 'stock-badge';
            badge.innerHTML = `
                <i class="fas fa-fire"></i>
                Only ${stock} left!
            `;
            element.appendChild(badge);
        }
    });
}

// ============================================
// RECENTLY VIEWED PRODUCTS
// ============================================
class RecentlyViewed {
    constructor() {
        this.maxItems = 10;
        this.storageKey = 'recently_viewed';
    }
    
    addProduct(productId, productData) {
        let viewed = this.getViewed();
        
        // Remove if already exists
        viewed = viewed.filter(item => item.id !== productId);
        
        // Add to beginning
        viewed.unshift({
            id: productId,
            ...productData,
            viewedAt: new Date().toISOString()
        });
        
        // Keep only max items
        viewed = viewed.slice(0, this.maxItems);
        
        localStorage.setItem(this.storageKey, JSON.stringify(viewed));
        
        // Send to server
        this.syncToServer(productId);
    }
    
    getViewed() {
        const data = localStorage.getItem(this.storageKey);
        return data ? JSON.parse(data) : [];
    }
    
    syncToServer(productId) {
        fetch('/api/track_view', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ product_id: productId })
        }).catch(err => console.error('Failed to track view:', err));
    }
    
    displayRecentlyViewed(containerId) {
        const viewed = this.getViewed();
        const container = document.getElementById(containerId);
        
        if (!container || viewed.length === 0) return;
        
        container.innerHTML = `
            <h3 class="mb-4">Recently Viewed</h3>
            <div class="row g-3">
                ${viewed.slice(0, 4).map(product => `
                    <div class="col-md-3">
                        <div class="recently-viewed-card">
                            <img src="${product.image}" alt="${product.name}" class="img-fluid">
                            <h6>${product.name}</h6>
                            <p class="price">₹${product.price}</p>
                            <a href="/product/${product.id}" class="btn btn-sm btn-primary">View Again</a>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }
}

const recentlyViewed = new RecentlyViewed();

// ============================================
// PEOPLE VIEWING THIS PRODUCT
// ============================================
function showLiveViewers(productId) {
    const viewerCount = Math.floor(Math.random() * 20) + 5; // 5-25 viewers
    
    const badge = document.createElement('div');
    badge.className = 'live-viewers-badge';
    badge.innerHTML = `
        <div class="live-indicator-pulse"></div>
        <span>${viewerCount} people viewing this now</span>
    `;
    
    const productSection = document.querySelector('.product-detail');
    if (productSection) {
        productSection.insertBefore(badge, productSection.firstChild);
    }
}

// ============================================
// COUNTDOWN TIMER FOR DEALS
// ============================================
function initDealCountdown(endTime, elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    function updateCountdown() {
        const now = new Date().getTime();
        const distance = new Date(endTime).getTime() - now;
        
        if (distance < 0) {
            element.innerHTML = '<span class="deal-expired">Deal Expired</span>';
            return;
        }
        
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);
        
        element.innerHTML = `
            <div class="deal-countdown">
                <div class="countdown-item">
                    <span class="countdown-value">${String(hours).padStart(2, '0')}</span>
                    <span class="countdown-label">Hours</span>
                </div>
                <div class="countdown-separator">:</div>
                <div class="countdown-item">
                    <span class="countdown-value">${String(minutes).padStart(2, '0')}</span>
                    <span class="countdown-label">Minutes</span>
                </div>
                <div class="countdown-separator">:</div>
                <div class="countdown-item">
                    <span class="countdown-value">${String(seconds).padStart(2, '0')}</span>
                    <span class="countdown-label">Seconds</span>
                </div>
            </div>
        `;
    }
    
    updateCountdown();
    setInterval(updateCountdown, 1000);
}

// ============================================
// INITIALIZE ON PAGE LOAD
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    initStockCountdown();
    
    // Track current product view
    const productId = document.querySelector('[data-product-id]');
    if (productId) {
        const id = productId.dataset.productId;
        showLiveViewers(id);
        
        // Add to recently viewed
        const productData = {
            name: document.querySelector('.product-name')?.textContent,
            price: document.querySelector('.product-price')?.textContent,
            image: document.querySelector('.product-image')?.src
        };
        recentlyViewed.addProduct(id, productData);
    }
});
