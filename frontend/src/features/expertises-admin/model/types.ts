import type { ExpertiseStatus } from "@/entities/expertise";

export type ExpertiseAdminRecord = {
  id: number;
  customer_id: number;
  customer_name: string;
  expert_id: number | null;
  expert_name: string | null;
  object_code: string;
  area_code: string;
  hazard_class: number | null;
  expert_category: number;
  comment: string | null;
  status: ExpertiseStatus;
  price: string | null;
  created_at: string;
};

export type StatusGroup = "waiting" | "work" | "done";

export type StatusFilter = StatusGroup | "all";
