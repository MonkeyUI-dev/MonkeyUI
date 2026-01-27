import api from '../lib/api';

export const authService = {
  /**
   * Register a new user
   */
  register: async (name, email, password, passwordConfirm) => {
    const response = await api.post('/accounts/register/', {
      name,
      email,
      password,
      password_confirm: passwordConfirm,
    });
    
    if (response.data.tokens) {
      localStorage.setItem('access_token', response.data.tokens.access);
      localStorage.setItem('refresh_token', response.data.tokens.refresh);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    
    return response.data;
  },

  /**
   * Login user
   */
  login: async (email, password) => {
    const response = await api.post('/accounts/login/', {
      email,
      password,
    });
    
    if (response.data.access) {
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    
    return response.data;
  },

  /**
   * Logout user
   */
  logout: async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    try {
      await api.post('/accounts/logout/', {
        refresh_token: refreshToken,
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    }
  },

  /**
   * Get current user
   */
  getCurrentUser: async () => {
    const response = await api.get('/accounts/me/');
    return response.data.user;
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  },

  /**
   * Get stored user data
   */
  getUser: () => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },

  /**
   * Change password
   */
  changePassword: async (oldPassword, newPassword) => {
    const response = await api.put('/accounts/change-password/', {
      old_password: oldPassword,
      new_password: newPassword,
    });
    return response.data;
  },
};
