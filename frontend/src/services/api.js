const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";
const API_BASE = `${BACKEND_URL}/api`;

class ApiService {
  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const config = {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    };

    const response = await fetch(url, config);

    if (!response.ok) {
      const error = await response
        .json()
        .catch(() => ({ message: "Request failed" }));
      throw new Error(error.detail || error.message || "Request failed");
    }

    return response.json();
  }

  async get(endpoint, headers = {}) {
    return this.request(endpoint, { method: "GET", headers });
  }

  async post(endpoint, data, headers = {}) {
    return this.request(endpoint, {
      method: "POST",
      headers,
      body: JSON.stringify(data),
    });
  }

  async put(endpoint, data, headers = {}) {
    return this.request(endpoint, {
      method: "PUT",
      headers,
      body: JSON.stringify(data),
    });
  }

  async delete(endpoint, headers = {}) {
    return this.request(endpoint, { method: "DELETE", headers });
  }
}

export const apiService = new ApiService();
