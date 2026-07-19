import React, { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api, tokenStorage } from "../lib/api";

export interface CosibUser {
  id: string;
  email: string;
  username: string;
  full_name: string;
  role: "guest" | "student" | "lecturer" | "administrator" | "super_administrator";
  status: string;
  avatar_url: string | null;
}

interface AuthContextValue {
  user: CosibUser | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string, persist?: boolean) => Promise<void>;
  register: (payload: {
    email: string;
    username: string;
    password: string;
    full_name: string;
    matric_number?: string;
  }) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<CosibUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchMe = useCallback(async () => {
    if (!tokenStorage.getAccess()) {
      setIsLoading(false);
      return;
    }
    try {
      const { data } = await api.get<CosibUser>("/auth/me");
      setUser(data);
    } catch {
      tokenStorage.clear();
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMe();
  }, [fetchMe]);

  const login = useCallback(async (email: string, password: string, persist: boolean = true) => {
    const { data } = await api.post("/auth/login", { email, password });
    tokenStorage.set(data.access_token, data.refresh_token, persist);
    const me = await api.get<CosibUser>("/auth/me");
    setUser(me.data);
  }, []);

  const register = useCallback(
    async (payload: {
      email: string;
      username: string;
      password: string;
      full_name: string;
      matric_number?: string;
    }) => {
      await api.post("/auth/register", payload);
      await login(payload.email, payload.password);
    },
    [login]
  );

  const logout = useCallback(async () => {
    const refreshToken = tokenStorage.getRefresh();
    try {
      if (refreshToken) await api.post("/auth/logout", { refresh_token: refreshToken });
    } finally {
      tokenStorage.clear();
      setUser(null);
    }
  }, []);

  return (
    <AuthContext.Provider
      value={{ user, isLoading, isAuthenticated: !!user, login, register, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
