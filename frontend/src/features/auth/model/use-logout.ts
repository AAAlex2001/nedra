"use client";

import { useState } from "react";
import { logoutUser, useSession } from "@/entities/user";

export const useLogout = () => {
  const session = useSession();
  const [pending, setPending] = useState(false);

  const logout = async () => {
    setPending(true);

    try {
      await logoutUser();
    } finally {
      session.signOut();
      setPending(false);
    }
  };

  return { logout, pending };
};
