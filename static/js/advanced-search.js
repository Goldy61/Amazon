// ============================================
// ADVANCED SEARCH WITH FILTERS
// ============================================

class AdvancedSearch {
    constructor() {
        this.filters = {
            query: '',
            category: '',
            minPrice: 0,
            maxPrice: 100000,
            rating: 0,
            sortBy: 'relevance'
        };
        this.init();
    }
    
    init() {
        this.enhanceSearchBar();
        this.createFilterPanel();
        this.initVoiceSearch();
    }
    
    enhanceSearchBar() {
        const searchInput = document.querySelector('input[type="search"], input[name="q"]');
        if (!searchInput) return;
        
        // Add autocomplete
        searchInput.setAttribute('autocomplete', 'off');
        searchInput.addEventListener('input', (e) => this.handleSearchInput(e));
        searchInput.addEventListener('focus', () => this.showSearchSuggestions());
        
        // Create suggestions dropdown
        const suggestionsDiv = document.createElement('div');
        suggestionsDiv.className = 'search-suggestions';
        suggestionsDiv.id = 'search-suggestions';
        searchInput.parentElement.style.position = 'relative';
        searchInput.parentElement.appendChild(suggestionsDiv);
        
        // Close suggestions when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-suggestions') && !e.target.closest('input[type="search"]')) {
                this.hideSearchSuggestions();
            }
        });
    }
    
    handleSearchInput(e) {
        const query = e.target.value.trim();
        this.filters.query = query;
        
        if (query.length >= 2) {
            this.fetchSuggestions(query);
        } else {
            this.hideSearchSuggestions();
        }
    }
    
    async fetchSuggestions(query) {
        try {
            const response = await fetch(`/api/search_suggestions?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            this.displaySuggestions(data.suggestions || []);
        } catch (error) {
            console.error('Failed to fetch suggestions:', error);
            // Fallback to local suggestions
            this.displayLocalSuggestions(query);
        }
    }
    
    displayLocalSuggestions(query) {
        const suggestions = [
            'Wireless Headphones',
            'Smart Watch',
            'Gaming Laptop',
            'Running Shoes',
            'Bluetooth Speaker',
            'Camera',
            'Phone Case',
            'Backpack'
        ].filter(item => item.toLowerCase().includes(query.toLowerCase()));
        
        this.displaySuggestions(suggestions);
    }
    
    displaySuggestions(suggestions) {
        const suggestionsDiv = document.getElementById('search-suggestions');
        if (!suggestionsDiv) return;
        
        if (suggestions.length === 0) {
            this.hideSearchSuggestions();
            return;
        }
        
        suggestionsDiv.innerHTML = suggestions.map(suggestion => `
            <div class="suggestion-item" onclick="advancedSearch.selectSuggestion('${suggestion}')">
                <i class="fas fa-search"></i>
                <span>${suggestion}</span>
            </div>
        `).join('');
        
        suggestionsDiv.classList.add('visible');
    }
    
    selectSuggestion(suggestion) {
        const searchInput = document.querySelector('input[type="search"], input[name="q"]');
        if (searchInput) {
            searchInput.value = suggestion;
            this.filters.query = suggestion;
            this.hideSearchSuggestions();
            this.performSearch();
        }
    }
    
    showSearchSuggestions() {
        const suggestionsDiv = document.getElementById('search-suggestions');
        if (suggestionsDiv && suggestionsDiv.children.length > 0) {
            suggestionsDiv.classList.add('visible');
        }
    }
    
    hideSearchSuggestions() {
        const suggestionsDiv = document.getElementById('search-suggestions');
        if (suggestionsDiv) {
            suggestionsDiv.classList.remove('visible');
        }
    }
    
    createFilterPanel() {
        const filterButton = document.createElement('button');
        filterButton.className = 'btn-filter-toggle';
        filterButton.innerHTML = '<i class="fas fa-filter"></i> Filters';
        filterButton.onclick = () => this.toggleFilterPanel();
        
        // Add to page (adjust selector based on your layout)
        const productsHeader = document.querySelector('.products-header, .section-header');
        if (productsHeader) {
            productsHeader.appendChild(filterButton);
        }
        
        // Create filter panel
        const filterPanel = document.createElement('div');
        filterPanel.className = 'filter-panel';
        filterPanel.id = 'filter-panel';
        filterPanel.innerHTML = `
            <div class="filter-panel-content">
                <div class="filter-header">
                    <h4><i class="fas fa-sliders-h"></i> Filters</h4>
                    <button class="btn-close-filter" onclick="advancedSearch.toggleFilterPanel()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                
                <div class="filter-body">
                    <!-- Price Range -->
                    <div class="filter-group">
                        <h5>Price Range</h5>
                        <div class="price-range-inputs">
                            <input type="number" id="min-price" placeholder="Min" value="0" min="0">
                            <span>to</span>
                            <input type="number" id="max-price" placeholder="Max" value="100000" min="0">
                        </div>
                        <input type="range" id="price-slider" min="0" max="100000" step="100" value="100000">
                        <div class="price-range-display">
                            ₹<span id="price-display-min">0</span> - ₹<span id="price-display-max">100000</span>
                        </div>
                    </div>
                    
                    <!-- Rating Filter -->
                    <div class="filter-group">
                        <h5>Minimum Rating</h5>
                        <div class="rating-filter">
                            ${[5, 4, 3, 2, 1].map(rating => `
                                <label class="rating-option">
                                    <input type="radio" name="rating-filter" value="${rating}" ${rating === 0 ? 'checked' : ''}>
                                    <span class="rating-stars">
                                        ${this.generateStars(rating)}
                                    </span>
                                    <span class="rating-text">& Up</span>
                                </label>
                            `).join('')}
                        </div>
                    </div>
                    
                    <!-- Sort By -->
                    <div class="filter-group">
                        <h5>Sort By</h5>
                        <select id="sort-by" class="form-select">
                            <option value="relevance">Relevance</option>
                            <option value="price-low">Price: Low to High</option>
                            <option value="price-high">Price: High to Low</option>
                            <option value="rating">Customer Rating</option>
                            <option value="newest">Newest First</option>
                            <option value="popular">Most Popular</option>
                        </select>
                    </div>
                    
                    <!-- Category Filter -->
                    <div class="filter-group">
                        <h5>Category</h5>
                        <div class="category-filter" id="category-filter">
                            <!-- Categories will be loaded dynamically -->
                        </div>
                    </div>
                </div>
                
                <div class="filter-footer">
                    <button class="btn btn-outline-secondary" onclick="advancedSearch.resetFilters()">
                        <i class="fas fa-redo"></i> Reset
                    </button>
                    <button class="btn btn-primary" onclick="advancedSearch.applyFilters()">
                        <i class="fas fa-check"></i> Apply Filters
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(filterPanel);
        
        // Load categories
        this.loadCategories();
        
        // Add event listeners
        this.attachFilterListeners();
    }
    
    async loadCategories() {
        try {
            const response = await fetch('/api/categories');
            const data = await response.json();
            this.displayCategories(data.categories || []);
        } catch (error) {
            console.error('Failed to load categories:', error);
        }
    }
    
    displayCategories(categories) {
        const categoryFilter = document.getElementById('category-filter');
        if (!categoryFilter) return;
        
        categoryFilter.innerHTML = categories.map(cat => `
            <label class="category-option">
                <input type="checkbox" name="category" value="${cat.id}">
                <span>${cat.name}</span>
            </label>
        `).join('');
    }
    
    attachFilterListeners() {
        // Price range
        const minPrice = document.getElementById('min-price');
        const maxPrice = document.getElementById('max-price');
        const priceSlider = document.getElementById('price-slider');
        
        if (minPrice && maxPrice && priceSlider) {
            minPrice.addEventListener('input', () => this.updatePriceDisplay());
            maxPrice.addEventListener('input', () => this.updatePriceDisplay());
            priceSlider.addEventListener('input', (e) => {
                maxPrice.value = e.target.value;
                this.updatePriceDisplay();
            });
        }
    }
    
    updatePriceDisplay() {
        const minPrice = document.getElementById('min-price').value;
        const maxPrice = document.getElementById('max-price').value;
        
        document.getElementById('price-display-min').textContent = minPrice;
        document.getElementById('price-display-max').textContent = maxPrice;
    }
    
    toggleFilterPanel() {
        const panel = document.getElementById('filter-panel');
        if (panel) {
            panel.classList.toggle('visible');
        }
    }
    
    applyFilters() {
        // Collect filter values
        this.filters.minPrice = parseInt(document.getElementById('min-price').value) || 0;
        this.filters.maxPrice = parseInt(document.getElementById('max-price').value) || 100000;
        
        const ratingInput = document.querySelector('input[name="rating-filter"]:checked');
        this.filters.rating = ratingInput ? parseInt(ratingInput.value) : 0;
        
        this.filters.sortBy = document.getElementById('sort-by').value;
        
        const selectedCategories = Array.from(document.querySelectorAll('input[name="category"]:checked'))
            .map(cb => cb.value);
        this.filters.categories = selectedCategories;
        
        // Perform search with filters
        this.performSearch();
        this.toggleFilterPanel();
    }
    
    resetFilters() {
        this.filters = {
            query: this.filters.query,
            category: '',
            minPrice: 0,
            maxPrice: 100000,
            rating: 0,
            sortBy: 'relevance'
        };
        
        document.getElementById('min-price').value = 0;
        document.getElementById('max-price').value = 100000;
        document.getElementById('price-slider').value = 100000;
        document.getElementById('sort-by').value = 'relevance';
        
        document.querySelectorAll('input[name="rating-filter"]').forEach(input => {
            input.checked = false;
        });
        
        document.querySelectorAll('input[name="category"]').forEach(input => {
            input.checked = false;
        });
        
        this.updatePriceDisplay();
        this.performSearch();
    }
    
    performSearch() {
        const params = new URLSearchParams();
        
        if (this.filters.query) params.append('q', this.filters.query);
        if (this.filters.minPrice > 0) params.append('min_price', this.filters.minPrice);
        if (this.filters.maxPrice < 100000) params.append('max_price', this.filters.maxPrice);
        if (this.filters.rating > 0) params.append('rating', this.filters.rating);
        if (this.filters.sortBy !== 'relevance') params.append('sort', this.filters.sortBy);
        if (this.filters.categories && this.filters.categories.length > 0) {
            params.append('categories', this.filters.categories.join(','));
        }
        
        window.location.href = `/products?${params.toString()}`;
    }
    
    initVoiceSearch() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            return; // Voice search not supported
        }
        
        const searchInput = document.querySelector('input[type="search"], input[name="q"]');
        if (!searchInput) return;
        
        const voiceButton = document.createElement('button');
        voiceButton.className = 'btn-voice-search';
        voiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
        voiceButton.title = 'Voice Search';
        voiceButton.onclick = () => this.startVoiceSearch();
        
        searchInput.parentElement.appendChild(voiceButton);
    }
    
    startVoiceSearch() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        
        recognition.lang = 'en-US';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;
        
        const voiceButton = document.querySelector('.btn-voice-search');
        voiceButton.classList.add('listening');
        voiceButton.innerHTML = '<i class="fas fa-circle"></i>';
        
        recognition.start();
        
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            const searchInput = document.querySelector('input[type="search"], input[name="q"]');
            if (searchInput) {
                searchInput.value = transcript;
                this.filters.query = transcript;
                this.performSearch();
            }
        };
        
        recognition.onerror = (event) => {
            console.error('Voice search error:', event.error);
            voiceButton.classList.remove('listening');
            voiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
        };
        
        recognition.onend = () => {
            voiceButton.classList.remove('listening');
            voiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
        };
    }
    
    generateStars(rating) {
        let stars = '';
        for (let i = 0; i < rating; i++) {
            stars += '<i class="fas fa-star"></i>';
        }
        for (let i = rating; i < 5; i++) {
            stars += '<i class="far fa-star"></i>';
        }
        return stars;
    }
}

// Initialize
let advancedSearch;
document.addEventListener('DOMContentLoaded', () => {
    advancedSearch = new AdvancedSearch();
});
