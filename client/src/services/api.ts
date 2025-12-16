import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface RemoveBgRequest {
  image_file_b64?: string;
  image_url?: string;
  size?: string;
  type?: string;
  type_level?: string;
  format?: string;
  roi?: string;
  crop?: boolean;
  crop_margin?: string;
  scale?: string;
  position?: string;
  channels?: string;
  add_shadow?: boolean;
  shadow_type?: string;
  shadow_opacity?: string;
  semitransparency?: boolean;
  bg_color?: string;
  bg_image_url?: string;
}

export interface RemoveBgResponse {
  data: {
    result_b64: string;
    foreground_top: number;
    foreground_left: number;
    foreground_width: number;
    foreground_height: number;
  };
}

export interface RemoveBgError {
  errors: Array<{
    code: string;
    title: string;
  }>;
}

export const removeBackground = async (
  request: RemoveBgRequest
): Promise<RemoveBgResponse> => {
  const response = await api.post<RemoveBgResponse>('/removebg', request);
  return response.data;
};

export const checkHealth = async () => {
  const response = await api.get('/');
  return response.data;
};

export default api;

