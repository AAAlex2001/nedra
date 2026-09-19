import type { ApplicationStatus, ExpertApplicationRecord } from "@/entities/expert";

export type StatusFilter = ApplicationStatus | "all";

export type ApplicationsState = {
  items: ExpertApplicationRecord[];
  filter: StatusFilter;
  pendingId: number | null;
  refreshing: boolean;
  error: string | null;
};

export type ApplicationsAction =
  | { type: "filter/set"; filter: StatusFilter }
  | { type: "review/start"; id: number }
  | { type: "review/success"; item: ExpertApplicationRecord }
  | { type: "review/error"; message: string }
  | { type: "refresh/start" }
  | { type: "refresh/success"; items: ExpertApplicationRecord[] }
  | { type: "refresh/error"; message: string };
