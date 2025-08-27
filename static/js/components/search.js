/**
 * Search Component for Afèpanou
 * Handles search functionality, autocomplete, and filters
 */

class SearchComponent {
    constructor(options = {}) {
        this.options = {
            searchInputId: 'search-input',
            suggestionsId: 'search-suggestions',
            filtersToggleId: 'filters-toggle',
            filtersId: 'search-filters',
            debounceDelay: 300,
            minQueryLength: 2,
            ...options
        };
        
        this.searchInput = document.getElementById(this.options.searchInputId);
        this.suggestionsContainer = document.getElementById(this.options.suggestionsId);
        this.filtersToggle = document.getElementById(this.options.filtersToggleId);
        this.filtersContainer = document.getElementById(this.options.filtersId);
        
        this.debounceTimer = null;
        this.currentFocus = -1;
        this.suggestions = [];
        
        this.init();
    }
    
    init() {
        if (!this.searchInput) return;
        
        this.bindEvents();
        this.setupAccessibility();
    }
    
    bindEvents() {
        // Search input events
        this.searchInput.addEventListener('input', (e) => {
            this.handleInput(e.target.value);
        });
        
        this.searchInput.addEventListener('keydown', (e) => {
            this.handleKeydown(e);
        });
        
        this.searchInput.addEventListener('focus', () => {
            this.showSuggestions();
        });
        
        // Filters toggle
        if (this.filtersToggle && this.filtersContainer) {
            this.filtersToggle.addEventListener('click', () => {
                this.toggleFilters();
            });
        }
        
        // Click outside to close suggestions
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-bar')) {
                this.hideSuggestions();
            }
        });
        
        // Handle form submission
        const searchForm = this.searchInput.closest('form');
        if (searchForm) {
            searchForm.addEventListener('submit', (e) => {
                this.handleSubmit(e);
            });
        }
    }
    
    setupAccessibility() {
        // Add ARIA attributes
        this.searchInput.setAttribute('role', 'combobox');
        this.searchInput.setAttribute('aria-expanded', 'false');
        this.searchInput.setAttribute('aria-autocomplete', 'list');
        
        if (this.suggestionsContainer) {
            this.suggestionsContainer.setAttribute('role', 'listbox');
        }
    }
    
    handleInput(query) {
        clearTimeout(this.debounceTimer);
        
        if (query.length < this.options.minQueryLength) {
            this.hideSuggestions();
            return;
        }
        
        this.debounceTimer = setTimeout(() => {
            this.fetchSuggestions(query);
        }, this.options.debounceDelay);
    }
    
    handleKeydown(e) {
        if (!this.suggestionsContainer || this.suggestions.length === 0) return;
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.currentFocus++;
                if (this.currentFocus >= this.suggestions.length) {
                    this.currentFocus = 0;
                }
                this.updateFocus();
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                this.currentFocus--;
                if (this.currentFocus < 0) {
                    this.currentFocus = this.suggestions.length - 1;
                }
                this.updateFocus();
                break;
                
            case 'Enter':
                e.preventDefault();
                if (this.currentFocus >= 0) {
                    this.selectSuggestion(this.suggestions[this.currentFocus]);
                } else {
                    this.searchInput.closest('form').submit();
                }
                break;
                
            case 'Escape':
                this.hideSuggestions();
                break;
        }
    }
    
    handleSubmit(e) {
        this.hideSuggestions();
        
        // Add search analytics
        this.trackSearch(this.searchInput.value);
    }
    
    async fetchSuggestions(query) {
        try {
            const response = await fetch(`/api/search/suggestions/?q=${encodeURIComponent(query)}`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json',
                }
            });
            
            if (!response.ok) throw new Error('Failed to fetch suggestions');
            
            const data = await response.json();
            this.suggestions = data.suggestions || [];
            this.displaySuggestions();
            
        } catch (error) {
            console.error('Search suggestions error:', error);
            this.suggestions = [];
            this.hideSuggestions();
        }
    }
    
    displaySuggestions() {
        if (!this.suggestionsContainer || this.suggestions.length === 0) {
            this.hideSuggestions();
            return;
        }
        
        const suggestionsList = this.suggestionsContainer.querySelector('#suggestions-list');
        if (!suggestionsList) return;
        
        suggestionsList.innerHTML = '';
        
        this.suggestions.forEach((suggestion, index) => {
            const li = document.createElement('li');
            li.className = 'suggestion-item';
            li.setAttribute('role', 'option');
            li.setAttribute('id', `suggestion-${index}`);
            
            li.innerHTML = `
                <div class="suggestion-content">
                    <i class="fas ${this.getSuggestionIcon(suggestion.type)}" aria-hidden="true"></i>
                    <div class="suggestion-text">
                        <div class="suggestion-title">${this.highlightQuery(suggestion.title)}</div>
                        ${suggestion.subtitle ? `<div class="suggestion-subtitle">${suggestion.subtitle}</div>` : ''}
                    </div>
                    ${suggestion.count ? `<div class="suggestion-count">${suggestion.count}</div>` : ''}
                </div>
            `;
            
            li.addEventListener('click', () => {
                this.selectSuggestion(suggestion);
            });
            
            li.addEventListener('mouseenter', () => {
                this.currentFocus = index;
                this.updateFocus();
            });
            
            suggestionsList.appendChild(li);
        });
        
        this.showSuggestions();
    }
    
    showSuggestions() {
        if (this.suggestionsContainer) {
            this.suggestionsContainer.style.display = 'block';
            this.searchInput.setAttribute('aria-expanded', 'true');
        }
    }
    
    hideSuggestions() {
        if (this.suggestionsContainer) {
            this.suggestionsContainer.style.display = 'none';
            this.searchInput.setAttribute('aria-expanded', 'false');
        }
        this.currentFocus = -1;
    }
    
    updateFocus() {
        const suggestionItems = this.suggestionsContainer.querySelectorAll('.suggestion-item');
        
        suggestionItems.forEach((item, index) => {
            if (index === this.currentFocus) {
                item.classList.add('suggestion-item--active');
                item.setAttribute('aria-selected', 'true');
                this.searchInput.setAttribute('aria-activedescendant', item.id);
            } else {
                item.classList.remove('suggestion-item--active');
                item.setAttribute('aria-selected', 'false');
            }
        });
    }
    
    selectSuggestion(suggestion) {
        if (suggestion.url) {
            // Navigate to suggestion URL
            window.location.href = suggestion.url;
        } else {
            // Fill search input and submit
            this.searchInput.value = suggestion.query || suggestion.title;
            this.hideSuggestions();
            this.searchInput.closest('form').submit();
        }
    }
    
    toggleFilters() {
        if (!this.filtersContainer) return;
        
        const isVisible = this.filtersContainer.style.display !== 'none';
        this.filtersContainer.style.display = isVisible ? 'none' : 'block';
        
        this.filtersToggle.setAttribute('aria-expanded', !isVisible);
        this.filtersToggle.classList.toggle('filters-toggle--active', !isVisible);
    }
    
    getSuggestionIcon(type) {
        const iconMap = {
            product: 'fa-box',
            category: 'fa-tag',
            seller: 'fa-store',
            brand: 'fa-certificate'
        };
        
        return iconMap[type] || 'fa-search';
    }
    
    highlightQuery(text) {
        const query = this.searchInput.value.trim();
        if (!query) return text;
        
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<strong>$1</strong>');
    }
    
    trackSearch(query) {
        // Analytics tracking
        if (typeof gtag !== 'undefined') {
            gtag('event', 'search', {
                search_term: query,
                page_location: window.location.href
            });
        }
        
        // Custom analytics
        this.sendAnalytics('search', {
            query: query,
            timestamp: new Date().toISOString(),
            page: window.location.pathname
        });
    }
    
    async sendAnalytics(event, data) {
        try {
            await fetch('/api/analytics/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value,
                },
                body: JSON.stringify({
                    event: event,
                    data: data
                })
            });
        } catch (error) {
            // Silently fail analytics
            console.debug('Analytics error:', error);
        }
    }
}

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('#search-input')) {
        new SearchComponent();
    }
});

// Export for manual initialization
window.SearchComponent = SearchComponent;