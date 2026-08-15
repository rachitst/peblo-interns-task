import axios from 'axios';

// Base API configuration
const api = axios.create({
  baseURL: '',
  headers: {
    'Content-Type': 'application/json',
  },
});

let currentRole = 'admin';

export const setApiRole = (role: 'editor' | 'admin') => {
  currentRole = role;
};

export const getApiRole = (): string => {
  return currentRole;
};

// Request interceptor to dynamically inject X-User-Role and X-Role headers
api.interceptors.request.use((config) => {
  config.headers['X-User-Role'] = currentRole;
  config.headers['X-Role'] = currentRole;
  return config;
});

// TypeScript Interfaces
export interface Artwork {
  id: string;
  episode_id: string;
  type: 'poster' | 'banner' | 'thumbnail';
  file_path: string;
  width?: number;
  height?: number;
  file_size_kb?: number;
  mime_type?: string;
  url?: string;
}

export interface Episode {
  id: string;
  season_id: string;
  content_group: string;
  episode_number: number;
  title: string;
  language: string;
  duration_sec: number;
  synopsis?: string;
  status: 'draft' | 'published';
  created_at: string;
  updated_at: string;
  artworks: Artwork[];
}

export interface Season {
  id: string;
  show_id: string;
  season_number: number;
  episodes: Episode[];
}

export interface Show {
  id: string;
  title: string;
  slug: string;
  section: string | null;
  synopsis?: string;
  categories: string[];
  created_at: string;
  updated_at: string;
  seasons: Season[];
}

export interface ValidationIssue {
  entity_type: 'show' | 'season' | 'episode' | 'artwork';
  entity_id: string;
  show_id?: string;
  show_title: string;
  season_number?: number;
  episode_id?: string;
  episode_number?: number;
  severity: 'blocker' | 'warning';
  code: string;
  message: string;
  fix_suggestion: string;
}

export interface ValidationReport {
  can_publish: boolean;
  total_blockers: number;
  total_warnings: number;
  summary: string;
  issues: ValidationIssue[];
  grouped_by_show: Record<string, ValidationIssue[]>;
}

export interface PublishRun {
  id: string;
  published_at: string;
  published_by: string;
  status: string;
  catalogue_version: number;
  shows_count: number;
  episodes_count: number;
  file_path: string;
  error_message?: string;
  metadata_json: Record<string, any>;
}

// API Methods
export const fetchShows = async (params?: { section?: string; search?: string }): Promise<Show[]> => {
  const { data } = await api.get('/admin/shows', { params });
  return data;
};

export const fetchShow = async (id: string): Promise<Show> => {
  const { data } = await api.get(`/admin/shows/${id}`);
  return data;
};

export const createShow = async (payload: Partial<Show>): Promise<Show> => {
  const { data } = await api.post('/admin/shows', payload);
  return data;
};

export const updateShow = async (id: string, payload: Partial<Show>): Promise<Show> => {
  const { data } = await api.patch(`/admin/shows/${id}`, payload);
  return data;
};

export const deleteShow = async (id: string): Promise<void> => {
  await api.delete(`/admin/shows/${id}`);
};

export const createSeason = async (showId: string, seasonNumber: number): Promise<Season> => {
  const { data } = await api.post(`/admin/shows/${showId}/seasons`, { season_number: seasonNumber });
  return data;
};

export const fetchEpisodes = async (params?: {
  status?: string;
  language?: string;
  search?: string;
}): Promise<Episode[]> => {
  const { data } = await api.get('/admin/episodes', { params });
  return data;
};

export const fetchEpisode = async (id: string): Promise<Episode> => {
  const { data } = await api.get(`/admin/episodes/${id}`);
  return data;
};

export const createEpisode = async (seasonId: string, payload: Partial<Episode>): Promise<Episode> => {
  const { data } = await api.post(`/admin/seasons/${seasonId}/episodes`, payload);
  return data;
};

export const updateEpisode = async (id: string, payload: Partial<Episode>): Promise<Episode> => {
  const { data } = await api.patch(`/admin/episodes/${id}`, payload);
  return data;
};

export const deleteEpisode = async (id: string): Promise<void> => {
  await api.delete(`/admin/episodes/${id}`);
};

export const uploadArtwork = async (
  episodeId: string,
  artworkType: 'poster' | 'banner' | 'thumbnail',
  file: File
): Promise<Artwork> => {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await api.post(`/admin/episodes/${episodeId}/artwork/${artworkType}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
};

export const fetchValidationReport = async (): Promise<ValidationReport> => {
  const { data } = await api.get('/admin/validation-report');
  return data;
};

export const triggerPublish = async (): Promise<any> => {
  const { data } = await api.post('/admin/catalog/publish');
  return data;
};

export const fetchPublishRuns = async (): Promise<PublishRun[]> => {
  const { data } = await api.get('/admin/publish-runs');
  return data;
};
