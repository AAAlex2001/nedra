"use client";

import { createContext, useContext, useState, type ReactNode } from "react";

type AuthModalValue = {
  open: boolean;
  openModal: () => void;
  closeModal: () => void;
};

const AuthModalContext = createContext<AuthModalValue | null>(null);

export const AuthModalProvider = ({ children }: { children: ReactNode }) => {
  const [open, setOpen] = useState(false);

  const openModal = () => setOpen(true);
  const closeModal = () => setOpen(false);

  return (
    <AuthModalContext.Provider value={{ open, openModal, closeModal }}>
      {children}
    </AuthModalContext.Provider>
  );
};

export const useAuthModal = (): AuthModalValue => {
  const value = useContext(AuthModalContext);

  if (!value) {
    throw new Error("useAuthModal можно вызывать только внутри AuthModalProvider");
  }

  return value;
};
