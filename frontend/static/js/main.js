// API конфигурация
const API_CONFIG = {
    baseURL: '/api',
    endpoints: {
        auth: {
            login: '/auth/login',
            register: '/auth/register',
            logout: '/auth/logout',
            refresh: '/auth/refresh',
            me: '/auth/me'
        },
        products: '/products',
        categories: '/categories',
        cart: '/cart',
        orders: '/orders'
    }
};

// Токен аутентификации
let authToken = localStorage.getItem('auth_token') || '';
let refreshToken = localStorage.getItem('refresh_token') || '';

// API клиент
const api = {
    async request(url, options = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (authToken) {
            headers['Authorization'] = `Bearer ${authToken}`;
        }

        const config = {
            ...options,
            headers,
            credentials: 'include' // Для работы с куками
        };

        try {
            const response = await fetch(`${API_CONFIG.baseURL}${url}`, config);

            if (response.status === 401 && refreshToken) {
                // Пробуем обновить токен
                const newTokens = await this.refreshAuthToken();
                if (newTokens) {
                    // Повторяем запрос с новым токеном
                    headers['Authorization'] = `Bearer ${newTokens.access}`;
                    const retryResponse = await fetch(`${API_CONFIG.baseURL}${url}`, {
                        ...config,
                        headers
                    });
                    return await this.handleResponse(retryResponse);
                }
            }

            return await this.handleResponse(response);
        } catch (error) {
            console.error('API request failed:', error);
            this.showNotification('Ошибка соединения с сервером', 'error');
            throw error;
        }
    },

    async handleResponse(response) {
        const contentType = response.headers.get('content-type');
        let data;

        if (contentType && contentType.includes('application/json')) {
            data = await response.json();
        } else {
            data = await response.text();
        }

        if (!response.ok) {
            const error = new Error(data.message || 'Ошибка сервера');
            error.status = response.status;
            error.data = data;
            throw error;
        }

        return data;
    },

    async refreshAuthToken() {
        try {
            const response = await fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.auth.refresh}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ refresh: refreshToken })
            });

            if (response.ok) {
                const tokens = await response.json();
                this.setAuthTokens(tokens);
                return tokens;
            }
        } catch (error) {
            console.error('Token refresh failed:', error);
            this.logout();
        }
        return null;
    },

    setAuthTokens(tokens) {
        authToken = tokens.access;
        if (tokens.refresh) {
            refreshToken = tokens.refresh;
        }

        localStorage.setItem('auth_token', authToken);
        localStorage.setItem('refresh_token', refreshToken);
    },

    clearAuthTokens() {
        authToken = '';
        refreshToken = '';
        localStorage.removeItem('auth_token');
        localStorage.removeItem('refresh_token');
    },

    // Auth методы
    async login(username, password) {
        const data = await this.request(API_CONFIG.endpoints.auth.login, {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });

        this.setAuthTokens(data);
        this.showNotification('Успешный вход!', 'success');
        return data;
    },

    async register(userData) {
        const data = await this.request(API_CONFIG.endpoints.auth.register, {
            method: 'POST',
            body: JSON.stringify(userData)
        });

        this.showNotification('Регистрация успешна!', 'success');
        return data;
    },

    async logout() {
        try {
            await this.request(API_CONFIG.endpoints.auth.logout, {
                method: 'POST'
            });
        } finally {
            this.clearAuthTokens();
            window.location.href = '/';
        }
    },

    // Product методы
    async getProducts(params = {}) {
        const query = new URLSearchParams(params).toString();
        const url = query ? `${API_CONFIG.endpoints.products}?${query}` : API_CONFIG.endpoints.products;
        return await this.request(url);
    },

    async getProduct(id) {
        return await this.request(`${API_CONFIG.endpoints.products}/${id}`);
    },

    async getCategories() {
        return await this.request(API_CONFIG.endpoints.categories);
    },

    // Cart методы
    async getCart() {
        return await this.request(API_CONFIG.endpoints.cart);
    },

    async addToCart(productId, quantity = 1) {
        return await this.request(API_CONFIG.endpoints.cart, {
            method: 'POST',
            body: JSON.stringify({ product_id: productId, quantity })
        });
    },

    async removeFromCart(itemId) {
        return await this.request(`${API_CONFIG.endpoints.cart}/${itemId}`, {
            method: 'DELETE'
        });
    },

    async updateCartItem(itemId, quantity) {
        return await this.request(`${API_CONFIG.endpoints.cart}/${itemId}`, {
            method: 'PUT',
            body: JSON.stringify({ quantity })
        });
    }
};

// Утилиты
const utils = {
    // Форматирование цены
    formatPrice(price) {
        return new Intl.NumberFormat('ru-RU', {
            style: 'currency',
            currency: 'KZT',
            minimumFractionDigits: 0
        }).format(price);
    },

    // Форматирование даты
    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('ru-RU');
    },

    // Создание звезд рейтинга
    createRatingStars(rating) {
        const fullStars = Math.floor(rating);
        const hasHalfStar = rating % 1 >= 0.5;
        let stars = '';

        for (let i = 0; i < 5; i++) {
            if (i < fullStars) {
                stars += '<i class="fas fa-star"></i>';
            } else if (i === fullStars && hasHalfStar) {
                stars += '<i class="fas fa-star-half-alt"></i>';
            } else {
                stars += '<i class="far fa-star"></i>';
            }
        }

        return stars;
    },

    // Показ уведомлений
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 
                                 type === 'error' ? 'exclamation-circle' : 
                                 type === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i>
                <span>${message}</span>
                <button class="notification-close"><i class="fas fa-times"></i></button>
            </div>
        `;

        document.body.appendChild(notification);

        // Анимация появления
        setTimeout(() => notification.classList.add('show'), 10);

        // Закрытие по кнопке
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        });

        // Автозакрытие
        setTimeout(() => {
            if (notification.parentNode) {
                notification.classList.remove('show');
                setTimeout(() => notification.remove(), 300);
            }
        }, 5000);
    },

    // Загрузка изображения
    loadImage(url, placeholder = '/static/images/placeholder.jpg') {
        return new Promise((resolve) => {
            const img = new Image();
            img.onload = () => resolve(url);
            img.onerror = () => resolve(placeholder);
            img.src = url;
        });
    }
};

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', async () => {
    try {
        // Загрузка категорий
        await loadCategories();

        // Инициализация поиска
        initSearch();

        // Инициализация корзины
        if (authToken) {
            await updateCartCount();
        }

        // Обработка выхода
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', async (e) => {
                e.preventDefault();
                await api.logout();
            });
        }

    } catch (error) {
        console.error('Initialization error:', error);
    }
});

// Функции загрузки данных
async function loadCategories() {
    try {
        const categories = await api.getCategories();

        // Обновляем выпадающее меню категорий
        const categoriesDropdown = document.getElementById('categories-dropdown');
        if (categoriesDropdown) {
            categoriesDropdown.innerHTML = categories.map(cat => `
                <a href="/category/${cat.id}/">${cat.name}</a>
            `).join('');
        }

        // Обновляем футер категории
        const footerCategories = document.getElementById('footer-categories');
        if (footerCategories) {
            footerCategories.innerHTML = categories.slice(0, 5).map(cat => `
                <li><a href="/category/${cat.id}/">${cat.name}</a></li>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

async function loadProducts(containerId, params = {}) {
    try {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = '<div class="loading">Загрузка товаров...</div>';

        const data = await api.getProducts(params);

        if (!data.items || data.items.length === 0) {
            container.innerHTML = '<div class="no-products">Товары не найдены</div>';
            return;
        }

        container.innerHTML = data.items.map(product => `
            <div class="product-card" data-id="${product.id}">
                ${product.discount ? `<span class="product-badge">-${product.discount}%</span>` : ''}
                <img src="${product.image || '/static/images/placeholder.jpg'}" 
                     alt="${product.name}" 
                     class="product-image"
                     loading="lazy">
                <div class="product-info">
                    <h3 class="product-title">${product.name}</h3>
                    <div class="product-rating">
                        ${utils.createRatingStars(product.rating || 0)}
                        <span class="rating-count">(${product.review_count || 0})</span>
                    </div>
                    <div class="product-price">
                        ${product.old_price ? 
                            `<span class="product-old-price">${utils.formatPrice(product.old_price)}</span>` : ''}
                        ${utils.formatPrice(product.price)}
                    </div>
                    <button class="btn-add-cart" onclick="addToCart(${product.id})">
                        <i class="fas fa-cart-plus"></i>
                        В корзину
                    </button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading products:', error);
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = '<div class="error">Ошибка загрузки товаров</div>';
        }
    }
}

// Поиск
function initSearch() {
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('global-search');

    if (searchForm && searchInput) {
        searchForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const query = searchInput.value.trim();

            if (query) {
                window.location.href = `/products/?search=${encodeURIComponent(query)}`;
            }
        });

        // Автодополнение (можно добавить позже)
    }
}

// Корзина
async function addToCart(productId) {
    try {
        if (!authToken) {
            utils.showNotification('Пожалуйста, войдите в систему', 'warning');
            window.location.href = '/login/';
            return;
        }

        await api.addToCart(productId);
        await updateCartCount();
        utils.showNotification('Товар добавлен в корзину!', 'success');
    } catch (error) {
        utils.showNotification(error.message || 'Ошибка добавления в корзину', 'error');
    }
}

async function updateCartCount() {
    try {
        const cart = await api.getCart();
        const cartCount = document.querySelector('.cart-count');

        if (cartCount) {
            const totalItems = cart.items.reduce((sum, item) => sum + item.quantity, 0);
            cartCount.textContent = totalItems;
            cartCount.style.display = totalItems > 0 ? 'inline' : 'none';
        }
    } catch (error) {
        console.error('Error updating cart count:', error);
    }
}

// Экспорт для использования в других файлах
window.api = api;
window.utils = utils;
window.loadProducts = loadProducts;
window.addToCart = addToCart;