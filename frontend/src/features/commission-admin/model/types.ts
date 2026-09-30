import type { CommissionApplicationRecord } from "@/entities/commission";

export type CommissionAdminState = {
  items: CommissionApplicationRecord[];
  pendingId: number | null;
  refreshing: boolean;
  error: string | null;
};

export type CommissionAdminAction =
  | { type: "delete/start"; id: number }
  | { type: "delete/success"; id: number }
  | { type: "delete/error"; message: string }
  | { type: "refresh/start" }
  | { type: "refresh/success"; items: CommissionApplicationRecord[] }
  | { type: "refresh/error"; message: string };
