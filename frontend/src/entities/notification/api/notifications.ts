import { API_URL, readErrorMessage } from "@/shared/api";
import type { Notification } from "../model/types";

export const fetchNotifications = async (): Promise<Notification[]> => {
  const response = await fetch(`${API_URL}/v1/notifications`, {
    credentials: "include",
    cache: "no-store",
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const items: Notification[] = await response.json();

  return items;
};

export const markNotificationRead = async (id: number): Promise<Notification> => {
  const response = await fetch(`${API_URL}/v1/notifications/${id}/read`, {
    method: "POST",
    credentials: "include",
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const updated: Notification = await response.json();

  return updated;
};

export const markAllNotificationsRead = async (
  expertiseIds?: number[],
): Promise<Notification[]> => {
  const response = await fetch(`${API_URL}/v1/notifications/read-all`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ expertise_ids: expertiseIds ?? null }),
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const items: Notification[] = await response.json();

  return items;
};
