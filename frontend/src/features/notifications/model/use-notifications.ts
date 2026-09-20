"use client";

import { useEffect, useState } from "react";
import {
  fetchNotifications,
  markAllNotificationsRead,
  markNotificationRead,
  type Notification,
} from "@/entities/notification";

const POLL_INTERVAL = 60_000;

type NotificationsState =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ready"; items: Notification[] };

export const useNotifications = () => {
  const [state, setState] = useState<NotificationsState>({ status: "loading" });
  const [pending, setPending] = useState(false);

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
    const timer = window.setInterval(() => void load(), POLL_INTERVAL);

    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, []);

  const items = state.status === "ready" ? state.items : [];
  const unreadItems = items.filter((item) => item.read_at === null);
  const unread = unreadItems.length;

  const linkedIds: number[] = [];
  for (const item of unreadItems) {
    if (item.expertise_id !== null && !linkedIds.includes(item.expertise_id)) {
      linkedIds.push(item.expertise_id);
    }
  }

  const unreadFor = (expertiseIds: number[]): number =>
    unreadItems.filter(
      (item) => item.expertise_id !== null && expertiseIds.includes(item.expertise_id),
    ).length;

  const markRead = async (id: number) => {
    if (state.status !== "ready") return;

    try {
      const updated = await markNotificationRead(id);
      setState({ status: "ready", items: items.map((item) => (item.id === id ? updated : item)) });
    } catch {
      return;
    }
  };

  const markAllRead = async (expertiseIds?: number[]) => {
    const target = expertiseIds === undefined ? unread : unreadFor(expertiseIds);
    if (state.status !== "ready" || target === 0) return;

    setPending(true);

    try {
      setState({ status: "ready", items: await markAllNotificationsRead(expertiseIds) });
    } catch {
      return;
    } finally {
      setPending(false);
    }
  };

  return { state, items, unread, linkedIds, unreadFor, pending, markRead, markAllRead };
};
