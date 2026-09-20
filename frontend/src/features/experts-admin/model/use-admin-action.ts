"use client";

import { useState } from "react";

const ACTION_FAILED = "Не удалось выполнить действие. Попробуйте ещё раз.";

export const useAdminAction = () => {
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = async (action: () => Promise<void>) => {
    setPending(true);
    setError(null);

    try {
      await action();
    } catch (caught) {
      const message = caught instanceof Error && caught.message ? caught.message : ACTION_FAILED;
      setError(message);
    } finally {
      setPending(false);
    }
  };

  return { pending, error, run };
};
