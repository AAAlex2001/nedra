"use client";

import { useEffect, useState } from "react";
import { fetchNotifications, markNotificationRead, type Notification } from "@/entities/notification";

type NotificationsState =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ready"; items: Notification[] };

export const useNotifications = () => {
  const [state, setState] = useState<NotificationsState>({ status: "loading" });

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      try {
        const items = await fetchNotifications();
        if (cancelled) return;

        setState({ status: "ready", items });
      } catch (error) {
        if (cancelled) return;

        const message =
          error instanceof Error && error.message ? error.message : "Не удалось загрузить уведомления";
        setState({ status: "error", message });
      }
    };

    void load();

    return () => {
      cancelled = true;
    };
  }, []);

  const markRead = async (id: number) => {
    if (state.status !== "ready") return;

    try {
      const updated = await markNotificationRead(id);
      const items = state.items.map((item) => (item.id === id ? updated : item));
      setState({ status: "ready", items });
    } catch {
      return;
    }
  };

  return { state, markRead };
};
