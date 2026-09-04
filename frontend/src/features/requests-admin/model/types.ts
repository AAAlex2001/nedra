import type { RequestRecord } from "@/entities/request";

export type RequestsState = {
  items: RequestRecord[];
  pendingId: number | null;
  refreshing: boolean;
  error: string | null;
};

export type RequestsAction =
  | { type: "delete/start"; id: number }
  | { type: "delete/success"; id: number }
  | { type: "delete/error"; message: string }
  | { type: "refresh/start" }
  | { type: "refresh/success"; items: RequestRecord[] }
  | { type: "refresh/error"; message: string }
  | { type: "error/clear" };
