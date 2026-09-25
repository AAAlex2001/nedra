"use client";

import { useState } from "react";
import {
  addMyCertificate,
  deleteMyCertificate,
  updateMyCertificate,
  type CertificateInput,
  type ExpertProfile,
} from "@/entities/expert";

const ACTION_FAILED = "Не удалось сохранить. Попробуйте ещё раз.";

export const useCertificates = (onChange: (profile: ExpertProfile) => void) => {
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = async (action: () => Promise<ExpertProfile>): Promise<boolean> => {
    setPending(true);
    setError(null);

    try {
      const profile = await action();
      onChange(profile);
      return true;
    } catch (caught) {
      const message = caught instanceof Error && caught.message ? caught.message : ACTION_FAILED;
      setError(message);
      return false;
    } finally {
      setPending(false);
    }
  };

  const add = (input: CertificateInput) => run(() => addMyCertificate(input));
  const update = (id: number, input: CertificateInput) =>
    run(() => updateMyCertificate(id, input));
  const remove = (id: number) => run(() => deleteMyCertificate(id));
  const clearError = () => setError(null);

  return { pending, error, add, update, remove, clearError };
};
