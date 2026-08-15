import axios from 'axios';

const api = axios.create({
  baseURL: '',
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface CatalogueArtworkMap {
  poster?: string;
  banner?: string;
  thumbnail?: string;
}

export interface CatalogueEpisodeVariant {
  episode_id: string;
  language: string;
  title: string;
  duration_sec: number;
  synopsis?: string;
}

export interface CatalogueEpisode {
  content_group: string;
  episode_number: number;
  title: string;
  duration_sec: number;
  synopsis?: string;
  languages: string[];
  artworks: CatalogueArtworkMap;
  variants: CatalogueEpisodeVariant[];
}

export interface CatalogueTrailer {
  episode_id: string;
  title: string;
  language: string;
  duration_sec: number;
  artworks: CatalogueArtworkMap;
}

export interface CatalogueSeason {
  season_number: number;
  episodes: CatalogueEpisode[];
}

export interface CatalogueShow {
  id: string;
  title: string;
  slug: string;
  section: string;
  categories: string[];
  synopsis?: string;
  artworks: CatalogueArtworkMap;
  trailers: CatalogueTrailer[];
  seasons: CatalogueSeason[];
  total_episodes: number;
}

export interface PublishedCatalogue {
  version: number;
  generated_at: string;
  generated_by: string;
  total_shows: number;
  total_episodes: number;
  sections: Record<string, CatalogueShow[]>;
}

export interface SearchResponse {
  query: string;
  matched_shows_count: number;
  matched_episodes_count: number;
  results: CatalogueShow[];
}

export const fetchCatalogue = async (): Promise<PublishedCatalogue> => {
  const { data } = await api.get('/catalog');
  return data;
};

export const searchCatalogue = async (params: {
  q?: string;
  category?: string;
  language?: string;
  section?: string;
}): Promise<SearchResponse> => {
  const { data } = await api.get('/catalog/search', { params });
  return data;
};

export const fetchShowDetail = async (idOrSlug: string): Promise<CatalogueShow> => {
  const { data } = await api.get(`/catalog/shows/${idOrSlug}`);
  return data;
};
