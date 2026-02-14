# Frontend Integration Guide - React Setup

## 📋 Prerequisites

Before starting frontend integration, ensure:
- Node.js (v16+) and npm installed
- React 18+ setup ready
- Axios or Fetch API knowledge
- Understanding of JWT authentication

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
npm install axios react-router-dom
```

**Optional (Recommended)**:
```bash
npm install redux react-redux @reduxjs/toolkit # for state management
npm install react-query # for data fetching
npm install date-fns # for date formatting
```

---

## 🔐 Authentication Setup

### 1. Create API Client

Create `src/api/axiosConfig.js`:

```javascript
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add JWT token to request headers
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle token refresh on 401
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');

      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/api/account/token/refresh/`, {
            refresh: refreshToken,
          });

          localStorage.setItem('access_token', response.data.access);
          originalRequest.headers.Authorization = `Bearer ${response.data.access}`;

          return apiClient(originalRequest);
        } catch (refreshError) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
```

### 2. Create `.env.local` in React Root

```
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_APP_NAME=Expense Tracker
```

---

## 📁 API Service Structure

Create `src/api/services/` directory with separate files for each module:

### `src/api/services/authService.js`

```javascript
import apiClient from '../axiosConfig';

export const authService = {
  register: (userData) =>
    apiClient.post('/api/account/register/', userData),

  verifyEmail: (email, otp) =>
    apiClient.post('/api/account/email-verify/', { email, otp }),

  login: (email, password) =>
    apiClient.post('/api/account/login/', { email, password }),

  refreshToken: (refreshToken) =>
    apiClient.post('/api/account/token/refresh/', { refresh: refreshToken }),

  requestPasswordReset: (email) =>
    apiClient.post('/api/account/password-reset/request/', { email }),

  verifyResetOTP: (email, otp) =>
    apiClient.post('/api/account/password-reset/verify-otp/', { email, otp }),

  confirmPasswordReset: (newPassword, confirmPassword) =>
    apiClient.post('/api/account/password-reset/confirm/', {
      new_password: newPassword,
      confirm_password: confirmPassword,
    }),

  getProfile: () =>
    apiClient.get('/api/account/profile/'),

  updateProfile: (profileData) =>
    apiClient.put('/api/account/profile/', profileData),
};
```

### `src/api/services/budgetService.js`

```javascript
import apiClient from '../axiosConfig';

export const budgetService = {
  getBudgets: (params = {}) =>
    apiClient.get('/api/budgets/', { params }),

  createBudget: (budgetData) =>
    apiClient.post('/api/budgets/', budgetData),

  getBudgetDetail: (id) =>
    apiClient.get(`/api/budgets/${id}/`),

  updateBudget: (id, budgetData) =>
    apiClient.put(`/api/budgets/${id}/`, budgetData),

  deleteBudget: (id) =>
    apiClient.delete(`/api/budgets/${id}/`),
};
```

### `src/api/services/expenseService.js`

```javascript
import apiClient from '../axiosConfig';

export const expenseService = {
  getExpenses: (params = {}) =>
    apiClient.get('/api/expenses/', { params }),

  createExpense: (expenseData) => {
    const formData = new FormData();
    Object.keys(expenseData).forEach((key) => {
      formData.append(key, expenseData[key]);
    });
    return apiClient.post('/api/expenses/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  getExpenseDetail: (id) =>
    apiClient.get(`/api/expenses/${id}/`),

  updateExpense: (id, expenseData) => {
    const formData = new FormData();
    Object.keys(expenseData).forEach((key) => {
      formData.append(key, expenseData[key]);
    });
    return apiClient.put(`/api/expenses/${id}/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  deleteExpense: (id) =>
    apiClient.delete(`/api/expenses/${id}/`),
};
```

### `src/api/services/dashboardService.js`

```javascript
import apiClient from '../axiosConfig';

export const dashboardService = {
  getDashboard: (params = {}) =>
    apiClient.get('/api/dashboard/', { params }),
};
```

### `src/api/services/settingsService.js`

```javascript
import apiClient from '../axiosConfig';

export const settingsService = {
  getSettings: () =>
    apiClient.get('/api/usersettings/'),

  updateSettings: (settingsData) =>
    apiClient.put('/api/usersettings/', settingsData),
};
```

---

## 🔄 State Management (Redux - Optional)

### `src/store/slices/authSlice.js`

```javascript
import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  user: null,
  accessToken: localStorage.getItem('access_token'),
  refreshToken: localStorage.getItem('refresh_token'),
  isLoading: false,
  error: null,
  isAuthenticated: !!localStorage.getItem('access_token'),
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setLoading: (state, action) => {
      state.isLoading = action.payload;
    },
    setUser: (state, action) => {
      state.user = action.payload;
      state.isAuthenticated = true;
    },
    setTokens: (state, action) => {
      state.accessToken = action.payload.access;
      state.refreshToken = action.payload.refresh;
      localStorage.setItem('access_token', action.payload.access);
      localStorage.setItem('refresh_token', action.payload.refresh);
      state.isAuthenticated = true;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
    logout: (state) => {
      state.user = null;
      state.accessToken = null;
      state.refreshToken = null;
      state.isAuthenticated = false;
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    },
  },
});

export const { setLoading, setUser, setTokens, setError, logout } = authSlice.actions;
export default authSlice.reducer;
```

---

## 📝 Component Examples

### Login Component

```javascript
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../api/services/authService';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await authService.login(email, password);
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
        required
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        required
      />
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
}
```

### Expenses List Component

```javascript
import React, { useState, useEffect } from 'react';
import { expenseService } from '../api/services/expenseService';

export default function ExpensesPage() {
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    category: '',
    date_from: '',
    date_to: '',
  });

  useEffect(() => {
    fetchExpenses();
  }, [filters]);

  const fetchExpenses = async () => {
    setLoading(true);
    try {
      const response = await expenseService.getExpenses(filters);
      setExpenses(response.data.results);
    } catch (error) {
      console.error('Failed to fetch expenses:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Expenses</h1>

      {/* Filters */}
      <input
        type="date"
        value={filters.date_from}
        onChange={(e) => setFilters({ ...filters, date_from: e.target.value })}
        placeholder="From Date"
      />
      <input
        type="date"
        value={filters.date_to}
        onChange={(e) => setFilters({ ...filters, date_to: e.target.value })}
        placeholder="To Date"
      />

      {/* Expenses List */}
      {loading ? (
        <p>Loading...</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Description</th>
              <th>Category</th>
              <th>Amount</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            {expenses.map((expense) => (
              <tr key={expense.id}>
                <td>{expense.description}</td>
                <td>{expense.category}</td>
                <td>${expense.amount}</td>
                <td>{new Date(expense.date).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
```

### Dashboard Component

```javascript
import React, { useState, useEffect } from 'react';
import { dashboardService } from '../api/services/dashboardService';

export default function DashboardPage() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    setLoading(true);
    try {
      const response = await dashboardService.getDashboard();
      setDashboard(response.data);
    } catch (error) {
      console.error('Failed to fetch dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <p>Loading...</p>;
  if (!dashboard) return <p>No data available</p>;

  return (
    <div>
      <h1>Dashboard</h1>

      <div className="stats">
        <div className="stat-card">
          <h3>Total Expenses</h3>
          <p>${dashboard.total_expenses}</p>
        </div>
        <div className="stat-card">
          <h3>Total Budgets</h3>
          <p>${dashboard.total_budgets}</p>
        </div>
        <div className="stat-card">
          <h3>Remaining</h3>
          <p>${dashboard.total_remaining}</p>
        </div>
      </div>

      <div className="charts">
        <h2>Top Categories</h2>
        {dashboard.top_categories.map((cat) => (
          <div key={cat.category}>
            <span>{cat.category}</span>
            <div className="progress-bar">
              <div style={{ width: `${cat.percentage}%` }}></div>
            </div>
            <span>${cat.amount}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 🔐 Protected Route Component

```javascript
import React from 'react';
import { Navigate } from 'react-router-dom';

export default function ProtectedRoute({ children }) {
  const isAuthenticated = !!localStorage.getItem('access_token');

  return isAuthenticated ? children : <Navigate to="/login" replace />;
}
```

### Usage in App.js

```javascript
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import ExpensesPage from './pages/ExpensesPage';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/expenses"
          element={
            <ProtectedRoute>
              <ExpensesPage />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
```

---

## 📋 File Upload Handling

For uploading files (profile picture, receipts):

```javascript
const handleFileUpload = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  // For profile picture
  formData.append('profile_picture', file);

  try {
    const response = await authService.updateProfile(formData);
    console.log('File uploaded:', response.data);
  } catch (error) {
    console.error('Upload failed:', error);
  }
};
```

---

## 🛠️ Error Handling Best Practices

```javascript
const handleApiCall = async () => {
  try {
    const response = await apiClient.get('/api/endpoint/');
    return response.data;
  } catch (error) {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    } else if (error.response?.status === 403) {
      // Handle forbidden
      console.error('Access denied');
    } else if (error.response?.status === 404) {
      // Handle not found
      console.error('Resource not found');
    } else if (error.response?.status >= 500) {
      // Handle server error
      console.error('Server error');
    } else {
      // Handle validation errors
      console.error(error.response?.data);
    }
  }
};
```

---

## 🌐 CORS Configuration Note

The backend is configured to accept requests from:
- `http://localhost:3000`
- `http://127.0.0.1:3000`

For production, update `CORS_ALLOWED_ORIGINS` in Django settings.

---

## ✅ Testing Checklist

- [ ] Login/Register flow works
- [ ] Token refresh works automatically
- [ ] Protected routes redirect to login when unauthenticated
- [ ] Expenses can be created, read, updated, deleted
- [ ] Budgets can be managed
- [ ] Dashboard loads data correctly
- [ ] File uploads work for profile pictures and receipts
- [ ] Error messages display properly
- [ ] Logout clears tokens and redirects

---

## 📞 Common Issues & Solutions

### Issue: CORS Error
**Solution**: Ensure backend CORS_ALLOWED_ORIGINS includes your frontend URL

### Issue: 401 Unauthorized on Protected Requests
**Solution**: Check if access token is properly stored and sent in Authorization header

### Issue: File Upload Returns 400
**Solution**: Use FormData for multipart requests and check file size limits

### Issue: Token Doesn't Refresh Automatically
**Solution**: Ensure refresh token is stored in localStorage and interceptor is properly configured

---

**Documentation Version**: 1.0
**Last Updated**: February 5, 2026
