// ============================================
// PRODUCT COMPARISON FUNCTIONALITY
// ============================================

class ProductComparison {
    constructor() {
        this.maxProducts = 3;
        this.comparisonList = [];
        this.init();
    }
    
    init() {
        // Load comparison list from session
        this.loadComparisonList();
        
        // Update UI
        this.updateComparisonBadge();
        
        // Add event listeners
        this.attachEventListeners();
    }
    
    attachEventListeners() {
        // Listen for compare button clicks
        document.addEventListener('click', (e) => {
            if (e.target.closest('.btn-compare')) {
                e.preventDefault();
                const btn = e.target.closest('.btn-compare');
                const productId = btn.dataset.productId;
                this.toggleProduct(productId);
            }
        });
    }
    
    async loadComparisonList() {
        try {
            const response = await fetch('/api/compare/list');
            const data = await response.json();
            
            if (data.success) {
                this.comparisonList = data.products.map(p => p.id.toString());
                this.updateComparisonBadge();
                this.updateCompareButtons();
            }
        } catch (error) {
            console.error('Error loading comparison list:', error);
        }
    }
    
    async toggleProduct(productId) {
        productId = productId.toString();
        
        if (this.comparisonList.includes(productId)) {
            await this.removeProduct(productId);
        } else {
            await this.addProduct(productId);
        }
    }
    
    async addProduct(productId) {
        if (this.comparisonList.length >= this.maxProducts) {
            this.showNotification(`Maximum ${this.maxProducts} products can be compared`, 'warning');
            return;
        }
        
        try {
            const response = await fetch('/api/compare/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ product_id: productId })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.comparisonList.push(productId);
                this.updateComparisonBadge();
                this.updateCompareButtons();
                this.showNotification('Product added to comparison', 'success');
                this.showComparisonBar();
            } else {
                this.showNotification(data.message, 'error');
            }
        } catch (error) {
            console.error('Error adding product:', error);
            this.showNotification('Failed to add product', 'error');
        }
    }
    
    async removeProduct(productId) {
        try {
            const response = await fetch('/api/compare/remove', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ product_id: productId })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.comparisonList = this.comparisonList.filter(id => id !== productId);
                this.updateComparisonBadge();
                this.updateCompareButtons();
                this.showNotification('Product removed from comparison', 'success');
                
                if (this.comparisonList.length === 0) {
                    this.hideComparisonBar();
                }
            } else {
                this.showNotification(data.message, 'error');
            }
        } catch (error) {
            console.error('Error removing product:', error);
            this.showNotification('Failed to remove product', 'error');
        }
    }
    
    updateComparisonBadge() {
        const badge = document.getElementById('comparisonBadge');
        if (badge) {
            badge.textContent = this.comparisonList.length;
            badge.style.display = this.comparisonList.length > 0 ? 'inline-block' : 'none';
        }
    }
    
    updateCompareButtons() {
        const buttons = document.querySelectorAll('.btn-compare');
        buttons.forEach(btn => {
            const productId = btn.dataset.productId;
            const isInComparison = this.comparisonList.includes(productId);
            
            if (isInComparison) {
                btn.classList.add('active');
                btn.innerHTML = '<i class="fas fa-check"></i> <span>In Comparison</span>';
            } else {
                btn.classList.remove('active');
                btn.innerHTML = '<i class="fas fa-balance-scale"></i> <span>Compare</span>';
            }
        });
    }
    
    showComparisonBar() {
        let bar = document.getElementById('comparisonBar');
        
        if (!bar) {
            bar = document.createElement('div');
            bar.id = 'comparisonBar';
            bar.className = 'comparison-bar';
            document.body.appendChild(bar);
        }
        
        const names = this.comparisonList.length;
        bar.innerHTML = `
            <div class="comparison-bar-content">
                <div class="comparison-info">
                    <i class="fas fa-balance-scale"></i>
                    <span>${names} product${names > 1 ? 's' : ''} selected for comparison</span>
                </div>
                <div class="comparison-actions">
                    <button class="btn btn-sm btn-light" onclick="productComparison.clearAll()">
                        <i class="fas fa-trash"></i> Clear
                    </button>
                    <a href="/compare" class="btn btn-sm btn-primary">
                        <i class="fas fa-eye"></i> Compare Now (${names})
                    </a>
                </div>
            </div>
        `;
        
        setTimeout(() => {
            bar.classList.add('show');
        }, 10);
    }
    
    hideComparisonBar() {
        const bar = document.getElementById('comparisonBar');
        if (bar) {
            bar.classList.remove('show');
            setTimeout(() => {
                bar.remove();
            }, 300);
        }
    }
    
    getComparisonUrl() {
        return this.comparisonList.map(id => `products=${id}`).join('&');
    }
    
    async clearAll() {
        if (confirm('Clear all products from comparison?')) {
            try {
                const response = await fetch('/api/compare/clear', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    this.comparisonList = [];
                    this.updateComparisonBadge();
                    this.updateCompareButtons();
                    this.hideComparisonBar();
                    this.showNotification('Comparison list cleared', 'success');
                }
            } catch (error) {
                console.error('Error clearing comparison:', error);
                this.showNotification('Failed to clear comparison', 'error');
            }
        }
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        
        const icon = type === 'success' ? 'check-circle' : 
                     type === 'error' ? 'exclamation-circle' : 
                     type === 'warning' ? 'exclamation-triangle' : 'info-circle';
        
        notification.innerHTML = `
            <i class="fas fa-${icon}"></i>
            <span>${message}</span>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }
}

// Initialize on page load
let productComparison;
document.addEventListener('DOMContentLoaded', function() {
    productComparison = new ProductComparison();
});

// Add styles
const comparisonStyles = document.createElement('style');
comparisonStyles.textContent = `
    /* Compare Button */
    .btn-compare {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 8px 16px;
        background: white;
        border: 2px solid #e5e7eb;
        color: #6b7280;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 14px;
        font-weight: 500;
    }
    
    .btn-compare:hover {
        border-color: #1E40AF;
        color: #1E40AF;
        transform: translateY(-2px);
    }
    
    .btn-compare.active {
        background: #1E40AF;
        border-color: #1E40AF;
        color: white;
    }
    
    .btn-compare i {
        font-size: 16px;
    }
    
    /* Comparison Badge */
    #comparisonBadge {
        position: absolute;
        top: -8px;
        right: -8px;
        background: #ef4444;
        color: white;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 11px;
        font-weight: 700;
        display: none;
    }
    
    /* Comparison Bar */
    .comparison-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(135deg, #1E40AF, #3B82F6);
        color: white;
        padding: 15px 20px;
        box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.2);
        z-index: 1000;
        transform: translateY(100%);
        transition: transform 0.3s ease;
    }
    
    .comparison-bar.show {
        transform: translateY(0);
    }
    
    .comparison-bar-content {
        max-width: 1200px;
        margin: 0 auto;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .comparison-info {
        display: flex;
        align-items: center;
        gap: 10px;
        font-weight: 600;
    }
    
    .comparison-info i {
        font-size: 20px;
    }
    
    .comparison-actions {
        display: flex;
        gap: 10px;
    }
    
    .comparison-actions .btn {
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .comparison-actions .btn:hover {
        transform: translateY(-2px);
    }
    
    /* Notification */
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        display: flex;
        align-items: center;
        gap: 10px;
        z-index: 10000;
        transform: translateX(400px);
        transition: transform 0.3s ease;
    }
    
    .notification.show {
        transform: translateX(0);
    }
    
    .notification-success {
        border-left: 4px solid #10b981;
    }
    
    .notification-success i {
        color: #10b981;
    }
    
    .notification-error {
        border-left: 4px solid #ef4444;
    }
    
    .notification-error i {
        color: #ef4444;
    }
    
    .notification-warning {
        border-left: 4px solid #f59e0b;
    }
    
    .notification-warning i {
        color: #f59e0b;
    }
    
    .notification-info {
        border-left: 4px solid #3b82f6;
    }
    
    .notification-info i {
        color: #3b82f6;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .comparison-bar-content {
            flex-direction: column;
            gap: 15px;
        }
        
        .comparison-actions {
            width: 100%;
        }
        
        .comparison-actions .btn {
            flex: 1;
        }
    }
    
    /* Dark Mode */
    body.dark-mode .btn-compare {
        background: #374151;
        border-color: #4b5563;
        color: #d1d5db;
    }
    
    body.dark-mode .btn-compare:hover {
        border-color: #60A5FA;
        color: #60A5FA;
    }
    
    body.dark-mode .notification {
        background: #1f2937;
        color: #f3f4f6;
    }
`;
document.head.appendChild(comparisonStyles);
