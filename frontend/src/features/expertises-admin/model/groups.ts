import type { ExpertiseStatus } from "@/entities/expertise";
import type { StatusFilter, StatusGroup } from "./types";

export const statusGroup = (status: ExpertiseStatus): StatusGroup => {
  if (status === "new") return "waiting";
  if (status === "accepted") return "done";

  return "work";
};

export const matchesFilter = (status: ExpertiseStatus, filter: StatusFilter): boolean =>
  filter === "all" || statusGroup(status) === filter;
