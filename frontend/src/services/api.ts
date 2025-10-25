/**
 * Service API pour communiquer avec le backend FastAPI
 */
import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Instance Axios configurée
const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface ProductResult {
  product_id: string;
  name: string;
  description?: string;
  price: number;
  image_url: string;
  score?: number;
  similarity?: number;
}

export interface SearchResponse {
  success: boolean;
  results: ProductResult[];
  total_results: number;
  search_type: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  models_loaded: boolean;
  redis_connected: boolean;
}

// API Functions

/**
 * Health check de l'API
 */
export const checkHealth = async (): Promise<HealthResponse> => {
  const response = await apiClient.get<HealthResponse>('/health');
  return response.data;
};

/**
 * Recherche par mots-clés
 */
export const searchByKeyword = async (
  query: string,
  topK: number = 10
): Promise<SearchResponse> => {
  const response = await apiClient.post<SearchResponse>('/search/keyword', {
    query,
    top_k: topK,
  });
  return response.data;
};

/**
 * Recherche par image (upload)
 */
export const searchByImageUpload = async (
  file: File,
  topK: number = 10
): Promise<SearchResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post<SearchResponse>(
    `/search/image/upload?top_k=${topK}`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  return response.data;
};

/**
 * Recherche par image (URL)
 */
export const searchByImageUrl = async (
  imageUrl: string,
  topK: number = 10
): Promise<SearchResponse> => {
  const response = await apiClient.post<SearchResponse>('/search/image/url', {
    image_url: imageUrl,
    top_k: topK,
  });
  return response.data;
};

export default apiClient;
