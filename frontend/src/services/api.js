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
      // Add timeout for simulation requests
      signal:
        endpoint === "/simulate"
          ? AbortSignal.timeout(30000) // 30 second timeout for simulations
          : AbortSignal.timeout(15000), // 15 second timeout for other requests
      ...options,
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const error = await response
          .json()
          .catch(() => ({ message: "Request failed" }));

        // Log detailed error information for debugging
        console.error("❌ API Error Response:", {
          status: response.status,
          statusText: response.statusText,
          url: response.url,
          error: error,
        });

        throw new Error(
          error.detail ||
            error.message ||
            `HTTP ${response.status}: ${response.statusText}`
        );
      }

      return response.json();
    } catch (error) {
      if (error.name === "AbortError") {
        throw new Error(
          "Request timed out. The simulation is taking longer than expected. Please try again."
        );
      }
      throw error;
    }
  }

  async get(endpoint, headers = {}) {
    return this.request(endpoint, { method: "GET", headers });
  }

  async post(endpoint, data, headers = {}) {
    const mergedHeaders = {
      "Content-Type": "application/json",
      ...headers
    };
    
    console.log("🔍 API POST Debug:", {
      endpoint,
      data,
      dataType: typeof data,
      isArray: Array.isArray(data),
      serialized: JSON.stringify(data),
      originalHeaders: headers,
      mergedHeaders
    });
    
    return this.request(endpoint, {
      method: "POST",
      headers: mergedHeaders,
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
