"use client";

import { useState } from "react";
import { switchRole, useSession, type UserRole } from "@/entities/user";

export const useRoleSwitch = () => {
  const session = useSession();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const select = async (role: UserRole) => {
    if (!session.user || session.user.role === role) return;

    setPending(true);
    setError(null);

    try {
      const user = await switchRole(role);
      session.signIn(user);
    } catch (caught) {
      const message =
        caught instanceof Error && caught.message ? caught.message : "Не удалось переключить роль";
      setError(message);
    } finally {
      setPending(false);
    }
  };

  return { select, pending, error };
};
