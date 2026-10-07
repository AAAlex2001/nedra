"use client";

import { useState } from "react";

const ACTION_FAILED = "Не удалось сохранить. Попробуйте ещё раз.";

export const useAction = () => {
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = async (action: () => Promise<void>): Promise<boolean> => {
    setPending(true);
    setError(null);

    try {
      await action();
      return true;
    } catch (caught) {
      const message = caught instanceof Error && caught.message ? caught.message : ACTION_FAILED;
      setError(message);
      return false;
    } finally {
      setPending(false);
    }
  };

  const reset = () => setError(null);

  return { pending, error, run, reset };
};
