import type { RequestRecord } from "@/entities/request";

export type RequestsState = {
  items: RequestRecord[];
  refreshing: boolean;
  error: string | null;
};

export type RequestsAction =
  | { type: "refresh/start" }
  | { type: "refresh/success"; items: RequestRecord[] }
  | { type: "refresh/error"; message: string };
