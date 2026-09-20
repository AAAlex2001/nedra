"use client";

import { createContext, useContext, useState, type ReactNode } from "react";
import type { User } from "./types";

type SessionStatus = "anonymous" | "authenticated";

type SessionState = {
  status: SessionStatus;
  user: User | null;
};

type SessionValue = SessionState & {
  signIn: (user: User) => void;
  signOut: () => void;
};

const SessionContext = createContext<SessionValue | null>(null);

const ANONYMOUS: SessionState = { status: "anonymous", user: null };

type SessionProviderProps = {
  initialUser: User | null;
  children: ReactNode;
};

export const SessionProvider = ({ initialUser, children }: SessionProviderProps) => {
  const initialState: SessionState = initialUser
    ? { status: "authenticated", user: initialUser }
    : ANONYMOUS;

  const [state, setState] = useState<SessionState>(initialState);

  const signIn = (user: User) => setState({ status: "authenticated", user });
  const signOut = () => setState(ANONYMOUS);

  return (
    <SessionContext.Provider value={{ ...state, signIn, signOut }}>
      {children}
    </SessionContext.Provider>
  );
};

export const useSession = (): SessionValue => {
  const value = useContext(SessionContext);

  if (!value) {
    throw new Error("useSession можно вызывать только внутри SessionProvider");
  }

  return value;
};
