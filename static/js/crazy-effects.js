// 🚀 CRAZY MODERN EFFECTS FOR SHOPHUB

// ============================================
// 1. PARTICLE BACKGROUND EFFECT
// ============================================
class ParticleBackground {
    constructor() {
        this.canvas = document.createElement('canvas');
        this.canvas.id = 'particle-canvas';
        this.canvas.style.position = 'fixed';
        this.canvas.style.top = '0';
        this.canvas.style.left = '0';
        this.canvas.style.width = '100%';
        this.canvas.style.height = '100%';
        this.canvas.style.zIndex = '-1';
        this.canvas.style.pointerEvents = 'none';
        document.body.prepend(this.canvas);
        
        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.particleCount = 50;
        
        this.resize();
        this.init();
        this.animate();
        
        window.addEventListener('resize', () => this.resize());
    }
    
    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }
    
    init() {
        for (let i = 0; i < this.particleCount; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                radius: Math.random() * 2 + 1
            });
        }
    }
    
    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.particles.forEach(particle => {
            particle.x += particle.vx;
            particle.y += particle.vy;
            
            if (particle.x < 0 || particle.x > this.canvas.width) particle.vx *= -1;
            if (particle.y < 0 || particle.y > this.canvas.height) particle.vy *= -1;
            
            this.ctx.beginPath();
            this.ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
            this.ctx.fillStyle = 'rgba(30, 64, 175, 0.3)';
            this.ctx.fill();
        });
        
        requestAnimationFrame(() => this.animate());
    }
}

// ============================================
// 2. CURSOR TRAIL EFFECT
// ============================================
class CursorTrail {
    constructor() {
        this.dots = [];
        this.maxDots = 15;
        this.mouseX = 0;
        this.mouseY = 0;
        
        document.addEventListener('mousemove', (e) => {
            this.mouseX = e.clientX;
            this.mouseY = e.clientY;
            this.addDot();
        });
        
        this.animate();
    }
    
    addDot() {
        const dot = document.createElement('div');
        dot.className = 'cursor-dot';
        dot.style.left = this.mouseX + 'px';
        dot.style.top = this.mouseY + 'px';
        document.body.appendChild(dot);
        
        this.dots.push(dot);
        
        if (this.dots.length > this.maxDots) {
            const oldDot = this.dots.shift();
            oldDot.remove();
        }
        
        setTimeout(() => {
            dot.style.opacity = '0';
            dot.style.transform = 'scale(0)';
        }, 10);
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
    }
}

// ============================================
// 3. SCROLL PROGRESS BAR
// ============================================
function initScrollProgress() {
    const progressBar = document.createElement('div');
    progressBar.id = 'scroll-progress';
    progressBar.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        height: 4px;
        background: linear-gradient(90deg, #1E40AF, #3B82F6, #60A5FA);
        z-index: 9999;
        transition: width 0.1s ease;
        box-shadow: 0 2px 10px rgba(30, 64, 175, 0.5);
    `;
    document.body.appendChild(progressBar);
    
    window.addEventListener('scroll', () => {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const scrollPercent = (scrollTop / scrollHeight) * 100;
        progressBar.style.width = scrollPercent + '%';
    });
}

// ============================================
// 4. FLOATING ACTION BUTTON (FAB)
// ============================================
function initFloatingButtons() {
    const fabContainer = document.createElement('div');
    fabContainer.className = 'fab-container';
    fabContainer.innerHTML = `
        <button class="fab-main" id="fabMain">
            <i class="fas fa-plus"></i>
        </button>
        <div class="fab-options" id="fabOptions">
            <button class="fab-option" onclick="scrollToTop()" title="Back to Top">
                <i class="fas fa-arrow-up"></i>
            </button>
            <button class="fab-option" onclick="window.location.href='/wishlist'" title="Wishlist">
                <i class="fas fa-heart"></i>
            </button>
            <button class="fab-option" onclick="window.location.href='/cart'" title="Cart">
                <i class="fas fa-shopping-cart"></i>
            </button>
            <button class="fab-option" onclick="toggleDarkMode()" title="Dark Mode">
                <i class="fas fa-moon"></i>
            </button>
        </div>
    `;
    document.body.appendChild(fabContainer);
    
    const fabMain = document.getElementById('fabMain');
    const fabOptions = document.getElementById('fabOptions');
    let isOpen = false;
    
    fabMain.addEventListener('click', () => {
        isOpen = !isOpen;
        fabOptions.classList.toggle('active', isOpen);
        fabMain.querySelector('i').className = isOpen ? 'fas fa-times' : 'fas fa-plus';
        fabMain.style.transform = isOpen ? 'rotate(45deg)' : 'rotate(0deg)';
    });
}

// ============================================
// 5. PRODUCT CARD TILT EFFECT
// ============================================
function initTiltEffect() {
    const cards = document.querySelectorAll('.modern-product-card');
    
    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateX = (y - centerY) / 10;
            const rotateY = (centerX - x) / 10;
            
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.05, 1.05, 1.05)`;
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)';
        });
    });
}

// ============================================
// 6. CONFETTI CELEBRATION
// ============================================
function launchConfetti() {
    const duration = 3 * 1000;
    const animationEnd = Date.now() + duration;
    const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 9999 };
    
    function randomInRange(min, max) {
        return Math.random() * (max - min) + min;
    }
    
    const interval = setInterval(function() {
        const timeLeft = animationEnd - Date.now();
        
        if (timeLeft <= 0) {
            return clearInterval(interval);
        }
        
        const particleCount = 50 * (timeLeft / duration);
        
        // Create confetti particles
        for (let i = 0; i < particleCount; i++) {
            const confetti = document.createElement('div');
            confetti.className = 'confetti-particle';
            confetti.style.left = Math.random() * 100 + '%';
            confetti.style.backgroundColor = `hsl(${Math.random() * 360}, 100%, 50%)`;
            document.body.appendChild(confetti);
            
            setTimeout(() => confetti.remove(), 3000);
        }
    }, 250);
}

// ============================================
// 7. TYPING EFFECT FOR HERO TEXT
// ============================================
function initTypingEffect() {
    const heroTitle = document.querySelector('.hero-title');
    if (!heroTitle) return;
    
    const originalText = heroTitle.textContent;
    heroTitle.textContent = '';
    let i = 0;
    
    function typeWriter() {
        if (i < originalText.length) {
            heroTitle.textContent += originalText.charAt(i);
            i++;
            setTimeout(typeWriter, 100);
        }
    }
    
    setTimeout(typeWriter, 500);
}

// ============================================
// 8. SMOOTH SCROLL WITH EASING
// ============================================
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// ============================================
// 9. LIVE VISITOR COUNTER
// ============================================
function initLiveCounter() {
    const counter = document.createElement('div');
    counter.className = 'live-counter';
    counter.innerHTML = `
        <div class="live-indicator-dot"></div>
        <span id="visitorCount">0</span> people shopping now
    `;
    document.body.appendChild(counter);
    
    // Simulate live count
    let count = Math.floor(Math.random() * 50) + 20;
    document.getElementById('visitorCount').textContent = count;
    
    setInterval(() => {
        count += Math.floor(Math.random() * 5) - 2;
        count = Math.max(10, Math.min(100, count));
        document.getElementById('visitorCount').textContent = count;
    }, 5000);
}

// ============================================
// 10. FLASH SALE TIMER
// ============================================
function initFlashSaleTimer() {
    const timer = document.createElement('div');
    timer.className = 'flash-sale-timer';
    timer.innerHTML = `
        <div class="timer-content">
            <i class="fas fa-bolt"></i>
            <span>Flash Sale Ends In:</span>
            <div class="timer-digits">
                <div class="timer-box">
                    <span id="hours">00</span>
                    <small>Hours</small>
                </div>
                <div class="timer-box">
                    <span id="minutes">00</span>
                    <small>Minutes</small>
                </div>
                <div class="timer-box">
                    <span id="seconds">00</span>
                    <small>Seconds</small>
                </div>
            </div>
        </div>
    `;
    
    const heroSection = document.querySelector('.modern-hero-section');
    if (heroSection) {
        heroSection.appendChild(timer);
    }
    
    // Set countdown to 2 hours from now
    const endTime = new Date().getTime() + (2 * 60 * 60 * 1000);
    
    function updateTimer() {
        const now = new Date().getTime();
        const distance = endTime - now;
        
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);
        
        document.getElementById('hours').textContent = String(hours).padStart(2, '0');
        document.getElementById('minutes').textContent = String(minutes).padStart(2, '0');
        document.getElementById('seconds').textContent = String(seconds).padStart(2, '0');
        
        if (distance < 0) {
            timer.remove();
        }
    }
    
    updateTimer();
    setInterval(updateTimer, 1000);
}

// ============================================
// 11. PRODUCT QUICK VIEW MODAL
// ============================================
function initQuickView() {
    const modal = document.createElement('div');
    modal.className = 'quick-view-modal';
    modal.id = 'quickViewModal';
    modal.innerHTML = `
        <div class="quick-view-content">
            <button class="quick-view-close" onclick="closeQuickView()">
                <i class="fas fa-times"></i>
            </button>
            <div id="quickViewBody"></div>
        </div>
    `;
    document.body.appendChild(modal);
}

function openQuickView(productId) {
    const modal = document.getElementById('quickViewModal');
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
    
    // Load product details via AJAX
    fetch(`/api/product/${productId}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('quickViewBody').innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <img src="${data.image_url}" class="img-fluid rounded" alt="${data.name}">
                    </div>
                    <div class="col-md-6">
                        <h3>${data.name}</h3>
                        <p class="text-muted">${data.description}</p>
                        <h4 class="text-primary">₹${data.price}</h4>
                        <button class="btn btn-primary" onclick="addToCart(${productId})">
                            Add to Cart
                        </button>
                    </div>
                </div>
            `;
        });
}

function closeQuickView() {
    const modal = document.getElementById('quickViewModal');
    modal.classList.remove('active');
    document.body.style.overflow = '';
}

// ============================================
// INITIALIZE ALL EFFECTS
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Initializing Crazy Effects...');
    
    // Initialize all effects
    new ParticleBackground();
    new CursorTrail();
    initScrollProgress();
    initFloatingButtons();
    initTiltEffect();
    initLiveCounter();
    initFlashSaleTimer();
    initQuickView();
    
    // Add confetti on first purchase
    window.addEventListener('purchase-success', () => {
        launchConfetti();
    });
    
    console.log('✨ All effects loaded!');
});
