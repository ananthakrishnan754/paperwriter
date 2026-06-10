// PaperWriter Auth Module
const API_BASE = '/api';

const Auth = {
    _token: null,
    _refreshToken: null,
    _user: null,

    init() {
        this._token = localStorage.getItem('pw_access_token');
        this._refreshToken = localStorage.getItem('pw_refresh_token');
        const userData = localStorage.getItem('pw_user');
        if (userData) {
            try { this._user = JSON.parse(userData); } catch { this._user = null; }
        }
    },

    getToken() { return this._token; },

    isAuthenticated() { return !!this._token; },

    getUser() { return this._user; },

    async check() {
        if (!this._token) return false;
        try {
            const res = await fetch(`${API_BASE}/auth/me/`, {
                headers: { 'Authorization': `Bearer ${this._token}` }
            });
            if (res.ok) {
                this._user = await res.json();
                localStorage.setItem('pw_user', JSON.stringify(this._user));
                return true;
            }
            if (res.status === 401 && this._refreshToken) {
                return await this._tryRefresh();
            }
            this.clear();
            return false;
        } catch {
            return false;
        }
    },

    async _tryRefresh() {
        try {
            const res = await fetch(`${API_BASE}/auth/refresh/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh: this._refreshToken }),
            });
            if (res.ok) {
                const data = await res.json();
                this._token = data.access;
                localStorage.setItem('pw_access_token', data.access);
                return true;
            }
            this.clear();
            return false;
        } catch {
            this.clear();
            return false;
        }
    },

    async login(username, password) {
        const res = await fetch(`${API_BASE}/auth/login/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Login failed');
        }
        const data = await res.json();
        this._token = data.access;
        this._refreshToken = data.refresh;
        localStorage.setItem('pw_access_token', data.access);
        localStorage.setItem('pw_refresh_token', data.refresh);
        await this.check();
        return this._user;
    },

    async register(username, email, password, password2) {
        const res = await fetch(`${API_BASE}/auth/register/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password, password2 }),
        });
        if (!res.ok) {
            const err = await res.json();
            const messages = Object.values(err).flat().join('. ');
            throw new Error(messages || 'Registration failed');
        }
    },

    clear() {
        this._token = null;
        this._refreshToken = null;
        this._user = null;
        localStorage.removeItem('pw_access_token');
        localStorage.removeItem('pw_refresh_token');
        localStorage.removeItem('pw_user');
    },

    logout() {
        this.clear();
        window.location.reload();
    },

    async apiFetch(url, options = {}) {
        const headers = options.headers || {};
        headers['Authorization'] = `Bearer ${this._token}`;
        if (!(options.body instanceof FormData)) {
            headers['Content-Type'] = 'application/json';
        }
        const res = await fetch(url, { ...options, headers });

        if (res.status === 401 && this._refreshToken) {
            const refreshed = await this._tryRefresh();
            if (refreshed) {
                headers['Authorization'] = `Bearer ${this._token}`;
                const retryRes = await fetch(url, { ...options, headers });
                return retryRes;
            }
            this.logout();
            throw new Error('Session expired');
        }
        return res;
    },

    async apiGet(url) {
        return this.apiFetch(url);
    },

    async apiPost(url, body) {
        return this.apiFetch(url, {
            method: 'POST',
            body: body instanceof FormData ? body : JSON.stringify(body),
        });
    },

    async apiPatch(url, body) {
        return this.apiFetch(url, {
            method: 'PATCH',
            body: JSON.stringify(body),
        });
    },

    async apiDelete(url) {
        return this.apiFetch(url, { method: 'DELETE' });
    },
};

// Auto-attach Authorization header to all API fetch calls
const originalFetch = window.fetch;
window.fetch = async function (url, options = {}) {
    if (typeof url === 'string' && url.startsWith(API_BASE)) {
        options = { ...options };
        options.headers = options.headers || {};
        if (Auth.getToken() && !options.headers['Authorization']) {
            options.headers['Authorization'] = `Bearer ${Auth.getToken()}`;
        }
    }
    const res = await originalFetch(url, options);

    if (res.status === 401 && Auth.getToken()) {
        const data = await res.clone().json().catch(() => ({}));
        if (data.code === 'token_not_valid') {
            const refreshed = await Auth._tryRefresh();
            if (refreshed) {
                options.headers['Authorization'] = `Bearer ${Auth.getToken()}`;
                return originalFetch(url, options);
            }
            Auth.logout();
        }
    }
    return res;
};

window.Auth = Auth;
