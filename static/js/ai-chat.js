// ============================================
// AI SHOPPING ASSISTANT CHAT
// ============================================

class AIChat {
    constructor() {
        this.messagesContainer = document.getElementById('chatMessages');
        this.chatInput = document.getElementById('chatInput');
        this.sendButton = document.getElementById('sendButton');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.quickSuggestions = document.getElementById('quickSuggestions');
        
        this.init();
    }
    
    init() {
        // Auto-focus input
        if (this.chatInput) {
            this.chatInput.focus();
        }
        
        // Scroll to bottom
        this.scrollToBottom();
    }
    
    async sendMessage(message) {
        if (!message || !message.trim()) return;
        
        // Add user message to chat
        this.addUserMessage(message);
        
        // Clear input
        this.chatInput.value = '';
        
        // Hide quick suggestions after first message
        if (this.quickSuggestions) {
            this.quickSuggestions.style.display = 'none';
        }
        
        // Show typing indicator
        this.showTyping();
        
        // Disable send button
        this.sendButton.disabled = true;
        
        try {
            // Send to API
            const response = await fetch('/api/chat/message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message })
            });
            
            const data = await response.json();
            
            // Hide typing indicator
            this.hideTyping();
            
            if (data.success) {
                // Add bot response
                this.addBotMessage(data.response, data.products);
            } else {
                this.addBotMessage('Sorry, I encountered an error. Please try again.', []);
            }
            
        } catch (error) {
            console.error('Chat error:', error);
            this.hideTyping();
            this.addBotMessage('Sorry, I could not connect to the server. Please try again.', []);
        } finally {
            // Re-enable send button
            this.sendButton.disabled = false;
            this.chatInput.focus();
        }
    }
    
    addUserMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user-message';
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-user"></i>
            </div>
            <div class="message-content">
                <div class="message-bubble">
                    <p>${this.escapeHtml(message)}</p>
                </div>
                <div class="message-time">${this.getCurrentTime()}</div>
            </div>
        `;
        
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    addBotMessage(message, products = []) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot-message';
        
        // Format message with markdown-like syntax
        const formattedMessage = this.formatMessage(message);
        
        let productsHtml = '';
        if (products && products.length > 0) {
            productsHtml = '<div class="chat-products">';
            products.forEach(product => {
                productsHtml += this.createProductCard(product);
            });
            productsHtml += '</div>';
        }
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="message-bubble">
                    ${formattedMessage}
                    ${productsHtml}
                </div>
                <div class="message-time">${this.getCurrentTime()}</div>
            </div>
        `;
        
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    createProductCard(product) {
        const price = product.discount_price || product.price;
        const originalPrice = product.discount_price ? product.price : null;
        const savings = originalPrice ? originalPrice - price : 0;
        
        // Generate star rating
        const rating = product.avg_rating || 0;
        const fullStars = Math.floor(rating);
        const hasHalfStar = rating % 1 >= 0.5;
        let starsHtml = '';
        
        for (let i = 0; i < fullStars; i++) {
            starsHtml += '<i class="fas fa-star"></i>';
        }
        if (hasHalfStar) {
            starsHtml += '<i class="fas fa-star-half-alt"></i>';
        }
        for (let i = fullStars + (hasHalfStar ? 1 : 0); i < 5; i++) {
            starsHtml += '<i class="far fa-star"></i>';
        }
        
        return `
            <div class="chat-product-card">
                <img src="${product.image_url}" class="product-image" alt="${this.escapeHtml(product.name)}">
                <div class="product-details">
                    <h6 class="product-name">${this.escapeHtml(product.name)}</h6>
                    <div class="product-price">
                        <span class="current-price">₹${price.toLocaleString('en-IN')}</span>
                        ${originalPrice ? `<span class="original-price">₹${originalPrice.toLocaleString('en-IN')}</span>` : ''}
                    </div>
                    ${savings > 0 ? `<div class="product-savings">Save ₹${savings.toLocaleString('en-IN')}</div>` : ''}
                    <div class="product-rating">
                        <span class="rating-stars">${starsHtml}</span>
                        <span class="rating-count">(${product.review_count || 0})</span>
                    </div>
                    <div class="product-stock ${product.in_stock ? 'in-stock' : 'out-of-stock'}">
                        ${product.in_stock ? '<i class="fas fa-check-circle"></i> In Stock' : '<i class="fas fa-times-circle"></i> Out of Stock'}
                    </div>
                    <div class="product-actions">
                        <a href="/product/${product.id}" class="btn btn-sm btn-primary">View Details</a>
                        ${product.in_stock ? `
                            <button class="btn btn-sm btn-outline-primary" onclick="addToCartFromChat(${product.id})">
                                <i class="fas fa-shopping-cart"></i>
                            </button>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }
    
    formatMessage(message) {
        // Convert markdown-like syntax to HTML
        let formatted = message;
        
        // Bold text **text**
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Italic text *text*
        formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Line breaks
        formatted = formatted.replace(/\n/g, '<br>');
        
        // Lists
        formatted = formatted.replace(/^- (.*?)$/gm, '<li>$1</li>');
        if (formatted.includes('<li>')) {
            formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
        }
        
        return formatted;
    }
    
    showTyping() {
        if (this.typingIndicator) {
            this.typingIndicator.style.display = 'flex';
            this.scrollToBottom();
        }
    }
    
    hideTyping() {
        if (this.typingIndicator) {
            this.typingIndicator.style.display = 'none';
        }
    }
    
    scrollToBottom() {
        if (this.messagesContainer) {
            setTimeout(() => {
                this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
            }, 100);
        }
    }
    
    getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit',
            hour12: true 
        });
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    clearHistory() {
        // Keep only welcome message
        const welcomeMessage = this.messagesContainer.querySelector('.bot-message');
        this.messagesContainer.innerHTML = '';
        if (welcomeMessage) {
            this.messagesContainer.appendChild(welcomeMessage);
        }
        
        // Show quick suggestions again
        if (this.quickSuggestions) {
            this.quickSuggestions.style.display = 'block';
        }
        
        this.scrollToBottom();
    }
}

// Initialize chat
let aiChat;
document.addEventListener('DOMContentLoaded', function() {
    aiChat = new AIChat();
});

// Global functions for template
function sendMessage(event) {
    event.preventDefault();
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (message && aiChat) {
        aiChat.sendMessage(message);
    }
}

function sendSuggestion(suggestion) {
    if (aiChat) {
        aiChat.sendMessage(suggestion);
    }
}

function clearChat() {
    if (confirm('Are you sure you want to clear the chat history?')) {
        if (aiChat) {
            aiChat.clearHistory();
        }
        
        // Call API to clear server-side history
        fetch('/api/chat/clear', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        }).catch(error => {
            console.error('Error clearing chat history:', error);
        });
    }
}

function toggleChatInfo() {
    const sidebar = document.getElementById('chatInfoSidebar');
    if (sidebar) {
        sidebar.classList.toggle('active');
    }
}

function toggleEmojiPicker() {
    // Placeholder for emoji picker functionality
    alert('Emoji picker coming soon!');
}

async function addToCartFromChat(productId) {
    try {
        const response = await fetch('/api/cart/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                product_id: productId,
                quantity: 1
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Product added to cart!', 'success');
            updateCartCount();
        } else {
            showNotification(data.message || 'Failed to add to cart', 'error');
        }
    } catch (error) {
        console.error('Error adding to cart:', error);
        showNotification('Failed to add to cart', 'error');
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Add to body
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

function updateCartCount() {
    // Update cart count in navbar
    fetch('/api/cart/count')
        .then(response => response.json())
        .then(data => {
            const cartBadge = document.querySelector('.cart-count');
            if (cartBadge && data.count !== undefined) {
                cartBadge.textContent = data.count;
            }
        })
        .catch(error => {
            console.error('Error updating cart count:', error);
        });
}

// Add notification styles
const notificationStyles = document.createElement('style');
notificationStyles.textContent = `
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
    
    .notification-info {
        border-left: 4px solid #3b82f6;
    }
    
    .notification-info i {
        color: #3b82f6;
    }
    
    .product-savings {
        color: #10b981;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 4px;
    }
    
    .product-stock {
        font-size: 12px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    
    .product-stock.in-stock {
        color: #10b981;
    }
    
    .product-stock.out-of-stock {
        color: #ef4444;
    }
    
    .chat-products {
        margin-top: 12px;
    }
`;
document.head.appendChild(notificationStyles);
