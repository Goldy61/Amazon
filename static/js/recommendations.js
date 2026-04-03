// ============================================
// PRODUCT RECOMMENDATION SYSTEM
// ============================================

class RecommendationEngine {
    constructor() {
        this.currentProductId = null;
        this.init();
    }
    
    init() {
        // Auto-load recommendations on product pages
        const productElement = document.querySelector('[data-product-id]');
        if (productElement) {
            this.currentProductId = productElement.dataset.productId;
            this.loadProductRecommendations();
            this.trackProductView();
        }
        
        // Load trending products on homepage
        if (document.getElementById('trending-products')) {
            this.loadTrendingProducts();
        }
        
        // Load personalized recommendations
        if (document.getElementById('personalized-recommendations')) {
            this.loadPersonalizedRecommendations();
        }
    }
    
    async loadProductRecommendations() {
        const container = document.getElementById('product-recommendations');
        if (!container || !this.currentProductId) return;
        
        try {
            // Show loading state
            container.innerHTML = this.getLoadingHTML();
            
            const response = await fetch(`/api/recommendations/${this.currentProductId}?limit=5`);
            const data = await response.json();
            
            if (data.success && data.recommendations.length > 0) {
                container.innerHTML = this.renderRecommendations(data.recommendations, 'Recommended for You');
            } else {
                container.innerHTML = this.getEmptyStateHTML();
            }
        } catch (error) {
            console.error('Failed to load recommendations:', error);
            container.innerHTML = this.getErrorHTML();
        }
    }
    
    async loadTrendingProducts() {
        const container = document.getElementById('trending-products');
        if (!container) return;
        
        try {
            container.innerHTML = this.getLoadingHTML();
            
            const response = await fetch('/api/recommendations/trending?limit=12');
            const data = await response.json();
            
            if (data.success && data.trending.length > 0) {
                container.innerHTML = this.renderRecommendations(data.trending, 'Trending Now 🔥');
            } else {
                container.innerHTML = this.getEmptyStateHTML();
            }
        } catch (error) {
            console.error('Failed to load trending products:', error);
            container.innerHTML = this.getErrorHTML();
        }
    }
    
    async loadPersonalizedRecommendations() {
        const container = document.getElementById('personalized-recommendations');
        if (!container) return;
        
        try {
            container.innerHTML = this.getLoadingHTML();
            
            const response = await fetch('/api/recommendations/personalized?limit=12');
            const data = await response.json();
            
            if (data.success && data.recommendations.length > 0) {
                container.innerHTML = this.renderRecommendations(data.recommendations, 'Picked Just for You ✨');
            } else {
                container.style.display = 'none';
            }
        } catch (error) {
            console.error('Failed to load personalized recommendations:', error);
            container.style.display = 'none';
        }
    }
    
    async trackProductView() {
        if (!this.currentProductId) return;
        
        try {
            await fetch(`/api/track-view/${this.currentProductId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
        } catch (error) {
            console.error('Failed to track view:', error);
        }
    }
    
    renderRecommendations(products, title) {
        return `
            <div class="recommendations-section">
                <div class="section-header mb-4">
                    <h3 class="section-title">${title}</h3>
                    <p class="section-subtitle">Based on your preferences and browsing history</p>
                </div>
                
                <div class="row g-4">
                    ${products.map(product => this.renderProductCard(product)).join('')}
                </div>
            </div>
        `;
    }
    
    renderProductCard(product) {
        const price = product.discount_price || product.price;
        const originalPrice = product.discount_price ? product.price : null;
        const discount = originalPrice ? Math.round(((originalPrice - price) / originalPrice) * 100) : 0;
        
        return `
            <div class="col-lg-3 col-md-4 col-sm-6" data-aos="fade-up">
                <div class="recommendation-card" onclick="window.location.href='/product/${product.id}'">
                    <div class="product-image-wrapper">
                        <img src="${product.image_url || '/static/images/placeholder.jpg'}" 
                             class="product-image" 
                             alt="${product.name}"
                             loading="lazy">
                        
                        ${discount > 0 ? `
                            <span class="discount-badge">${discount}% OFF</span>
                        ` : ''}
                        
                        ${product.reason ? `
                            <div class="recommendation-reason">
                                <i class="fas fa-lightbulb"></i>
                                <span>${product.reason}</span>
                            </div>
                        ` : ''}
                    </div>
                    
                    <div class="product-info">
                        <div class="product-category">${product.category_name}</div>
                        <h5 class="product-name">${this.truncate(product.name, 50)}</h5>
                        
                        ${product.avg_rating > 0 ? `
                            <div class="product-rating">
                                ${this.renderStars(product.avg_rating)}
                                <span class="rating-count">(${product.review_count})</span>
                            </div>
                        ` : ''}
                        
                        <div class="product-price">
                            <span class="price-current">₹${this.formatPrice(price)}</span>
                            ${originalPrice ? `
                                <span class="price-original">₹${this.formatPrice(originalPrice)}</span>
                            ` : ''}
                        </div>
                        
                        <div class="product-seller">
                            <i class="fas fa-store"></i>
                            ${product.business_name}
                        </div>
                        
                        ${product.trending_score ? `
                            <div class="trending-indicator">
                                <i class="fas fa-fire"></i>
                                <span>Trending</span>
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }
    
    renderStars(rating) {
        const fullStars = Math.floor(rating);
        const hasHalf = rating % 1 >= 0.5;
        let stars = '';
        
        for (let i = 0; i < fullStars; i++) {
            stars += '<i class="fas fa-star"></i>';
        }
        if (hasHalf) {
            stars += '<i class="fas fa-star-half-alt"></i>';
        }
        for (let i = fullStars + (hasHalf ? 1 : 0); i < 5; i++) {
            stars += '<i class="far fa-star"></i>';
        }
        
        return `<div class="rating-stars">${stars}</div>`;
    }
    
    getLoadingHTML() {
        return `
            <div class="recommendations-loading">
                <div class="row g-4">
                    ${Array(4).fill(0).map(() => `
                        <div class="col-lg-3 col-md-4 col-sm-6">
                            <div class="skeleton-card">
                                <div class="skeleton-image"></div>
                                <div class="skeleton-text"></div>
                                <div class="skeleton-text short"></div>
                                <div class="skeleton-text"></div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    getEmptyStateHTML() {
        return `
            <div class="empty-recommendations">
                <i class="fas fa-box-open fa-3x text-muted mb-3"></i>
                <h5>No recommendations available</h5>
                <p class="text-muted">Check back later for personalized suggestions</p>
            </div>
        `;
    }
    
    getErrorHTML() {
        return `
            <div class="error-recommendations">
                <i class="fas fa-exclamation-triangle fa-3x text-warning mb-3"></i>
                <h5>Unable to load recommendations</h5>
                <button class="btn btn-primary btn-sm" onclick="location.reload()">
                    <i class="fas fa-redo"></i> Try Again
                </button>
            </div>
        `;
    }
    
    truncate(text, length) {
        if (text.length <= length) return text;
        return text.substring(0, length) + '...';
    }
    
    formatPrice(price) {
        return parseFloat(price).toLocaleString('en-IN', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }
}

// Initialize recommendation engine
let recommendationEngine;
document.addEventListener('DOMContentLoaded', () => {
    recommendationEngine = new RecommendationEngine();
});

// ============================================
// RECOMMENDATION WIDGETS
// ============================================

// "Customers Also Bought" Widget
function loadAlsoBoughtWidget(productId, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    fetch(`/api/recommendations/${productId}?limit=4`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.recommendations.length > 0) {
                const filtered = data.recommendations.filter(r => 
                    r.reason && r.reason.includes('also bought')
                );
                
                if (filtered.length > 0) {
                    container.innerHTML = recommendationEngine.renderRecommendations(
                        filtered,
                        'Customers Also Bought'
                    );
                }
            }
        })
        .catch(error => console.error('Failed to load also bought:', error));
}

// "Similar Products" Widget
function loadSimilarProductsWidget(productId, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    fetch(`/api/recommendations/similar-price/${productId}?limit=4`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.similar.length > 0) {
                container.innerHTML = recommendationEngine.renderRecommendations(
                    data.similar,
                    'Similar Products'
                );
            }
        })
        .catch(error => console.error('Failed to load similar products:', error));
}

// Export for use in other scripts
window.RecommendationEngine = RecommendationEngine;
window.loadAlsoBoughtWidget = loadAlsoBoughtWidget;
window.loadSimilarProductsWidget = loadSimilarProductsWidget;
