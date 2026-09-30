"use client";

import { createContext, useContext, useState, type ReactNode } from "react";

const STORAGE_KEY = "nedra-commission-popup";

export type PopupStep = "intro" | "form";

type CommissionPopupValue = {
  open: boolean;
  step: PopupStep;
  openIntro: () => void;
  openForm: () => void;
  showStep: (step: PopupStep) => void;
  close: () => void;
};

const CommissionPopupContext = createContext<CommissionPopupValue | null>(null);

export const wasPopupClosed = (): boolean => {
  try {
    return window.localStorage.getItem(STORAGE_KEY) === "closed";
  } catch {
    return false;
  }
};

const rememberClosed = () => {
  try {
    window.localStorage.setItem(STORAGE_KEY, "closed");
  } catch {
    return;
  }
};

export const CommissionPopupProvider = ({ children }: { children: ReactNode }) => {
  const [open, setOpen] = useState(false);
  const [step, setStep] = useState<PopupStep>("intro");

  const openIntro = () => {
    setStep("intro");
    setOpen(true);
  };

  const openForm = () => {
    setStep("form");
    setOpen(true);
  };

  const close = () => {
    rememberClosed();
    setOpen(false);
  };

  return (
    <CommissionPopupContext.Provider
      value={{ open, step, openIntro, openForm, showStep: setStep, close }}
    >
      {children}
    </CommissionPopupContext.Provider>
  );
};

export const useCommissionPopup = (): CommissionPopupValue => {
  const value = useContext(CommissionPopupContext);

  if (!value) {
    throw new Error("useCommissionPopup можно вызывать только внутри CommissionPopupProvider");
  }

  return value;
};
