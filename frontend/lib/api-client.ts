type RequestConfig = {
  method?: 'GET' | 'POST' | 'PATCH' | 'DELETE' | 'PUT';
  headers?: Record<string, string>;
  body?: unknown;
  params?: Record<string, string | number | boolean | null | undefined>;
};

class ApiClient {
  private baseURL: string;

  constructor(
    baseURL: string = process.env.NEXT_PUBLIC_API_URL ||
      'http://localhost:8000',
  ) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    config: RequestConfig = {},
  ): Promise<T> {
    const { method = 'GET', headers = {}, body, params } = config;

    // Build URL with query parameters
    const url = new URL(`${this.baseURL}${endpoint}`);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== null && value !== undefined) {
          url.searchParams.append(key, String(value));
        }
      });
    }

    // Get auth token from Zustand store if available
    let authToken: string | null = null;
    if (typeof window !== 'undefined') {
      try {
        const storeData = localStorage.getItem('zustand-store');
        if (storeData) {
          const parsed = JSON.parse(storeData);
          authToken = parsed?.state?.authorization?.accessToken || null;
        }
      } catch {
        // Ignore parsing errors
      }
    }

    const requestHeaders: HeadersInit = {
      'Content-Type': 'application/json',
      ...headers,
    };

    if (authToken) {
      requestHeaders['Authorization'] = `Bearer ${authToken}`;
    }

    const requestConfig: RequestInit = {
      method,
      headers: requestHeaders,
    };

    if (body && method !== 'GET') {
      requestConfig.body = JSON.stringify(body);
    }

    const response = await fetch(url.toString(), requestConfig);

    if (!response.ok) {
      const errorData = await response
        .json()
        .catch(() => ({ detail: response.statusText }));
      throw new Error(
        errorData.detail || `HTTP error! status: ${response.status}`,
      );
    }

    // Handle empty responses
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return response.json();
    }

    return response.text() as unknown as T;
  }

  async get<T>(endpoint: string, params?: RequestConfig['params']): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET', params });
  }

  async post<T>(
    endpoint: string,
    body?: unknown,
    params?: RequestConfig['params'],
  ): Promise<T> {
    return this.request<T>(endpoint, { method: 'POST', body, params });
  }

  async patch<T>(
    endpoint: string,
    body?: unknown,
    params?: RequestConfig['params'],
  ): Promise<T> {
    return this.request<T>(endpoint, { method: 'PATCH', body, params });
  }

  async delete<T>(
    endpoint: string,
    params?: RequestConfig['params'],
  ): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE', params });
  }

  async put<T>(
    endpoint: string,
    body?: unknown,
    params?: RequestConfig['params'],
  ): Promise<T> {
    return this.request<T>(endpoint, { method: 'PUT', body, params });
  }
}

export const apiClient = new ApiClient();
