import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";

/**
 * The backend now lives on a different origin than the frontend in
 * production (Railway vs. Vercel), unlike same-origin setups where a
 * relative path would work. VITE_API_BASE_URL should be set to the full
 * Railway service URL (e.g. https://cosib-backend.up.railway.app) in production.
 * Left unset, requests fall back to a relative path, which only works
 * locally via the Vite dev server's proxy (see vite.config.ts).
 */
const API_ORIGIN = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");
export const API_BASE = `${API_ORIGIN}/api/v1`;

export const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

const TOKEN_KEY = "cosib_access_token";
const REFRESH_KEY = "cosib_refresh_token";

/**
 * Tokens live in localStorage by default (persists across browser
 * restarts — "remember me" checked). When the person logs in with
 * "remember me" unchecked, we use sessionStorage instead, so signing out
 * of the browser tab effectively signs out of COSIB.
 */
export const tokenStorage = {
  getAccess: () => localStorage.getItem(TOKEN_KEY) ?? sessionStorage.getItem(TOKEN_KEY),
  getRefresh: () => localStorage.getItem(REFRESH_KEY) ?? sessionStorage.getItem(REFRESH_KEY),
  set: (access: string, refresh: string, persist: boolean = true) => {
    const store = persist ? localStorage : sessionStorage;
    const other = persist ? sessionStorage : localStorage;
    store.setItem(TOKEN_KEY, access);
    store.setItem(REFRESH_KEY, refresh);
    other.removeItem(TOKEN_KEY);
    other.removeItem(REFRESH_KEY);
  },
  clear: () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
    sessionStorage.removeItem(TOKEN_KEY);
    sessionStorage.removeItem(REFRESH_KEY);
  },
};

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = tokenStorage.getAccess();
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let isRefreshing = false;
let pendingQueue: Array<() => void> = [];

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;

    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      const refreshToken = tokenStorage.getRefresh();
      if (!refreshToken) {
        tokenStorage.clear();
        window.location.href = "/login";
        return Promise.reject(error);
      }

      originalRequest._retry = true;

      if (isRefreshing) {
        // Wait for the in-flight refresh to finish, then retry.
        return new Promise((resolve) => {
          pendingQueue.push(() => resolve(api(originalRequest)));
        });
      }

      isRefreshing = true;
      try {
        const { data } = await axios.post(`${API_BASE}/auth/refresh`, { refresh_token: refreshToken });
        tokenStorage.set(data.access_token, data.refresh_token);
        pendingQueue.forEach((cb) => cb());
        pendingQueue = [];
        return api(originalRequest);
      } catch (refreshError) {
        tokenStorage.clear();
        window.location.href = "/login";
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);
