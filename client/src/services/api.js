// API service for communicating with Flask backend
const API_BASE_URL = 'http://localhost:5000';

class ApiService {
  // Generic request handler
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  // Health check
  async checkHealth() {
    return this.request('/health');
  }

  // User endpoints
  async getUsers() {
    return this.request('/api/users');
  }

  async getUser(userId) {
    return this.request(`/api/users/${userId}`);
  }

  async createUser(userData) {
    return this.request('/api/users', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  // Property endpoints
  async getProperties() {
    return this.request('/api/properties');
  }

  async getProperty(propertyId) {
    return this.request(`/api/properties/${propertyId}`);
  }

  async createProperty(propertyData) {
    return this.request('/api/properties', {
      method: 'POST',
      body: JSON.stringify(propertyData),
    });
  }

  async updateProperty(propertyId, propertyData) {
    return this.request(`/api/properties/${propertyId}`, {
      method: 'PUT',
      body: JSON.stringify(propertyData),
    });
  }

  async deleteProperty(propertyId) {
    return this.request(`/api/properties/${propertyId}`, {
      method: 'DELETE',
    });
  }

  // Simulation endpoints
  async runSimulation(propertyId, simulationParams = {}) {
    const { years = 10, strategy = 'hold' } = simulationParams;

    return this.request(`/api/properties/${propertyId}/simulate`, {
      method: 'POST',
      body: JSON.stringify({ years, strategy }),
    });
  }

  async getSimulations() {
    return this.request('/api/simulations');
  }

  async getSimulation(simulationId) {
    return this.request(`/api/simulations/${simulationId}`);
  }
}

// Create and export a singleton instance
const apiService = new ApiService();
export default apiService;