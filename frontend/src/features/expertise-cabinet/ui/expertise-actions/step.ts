import type { ReactNode } from "react";
import { formatRequestDate } from "@/entities/request";

export type Step = {
  text: string;
  action?: ReactNode;
  form?: ReactNode;
};

export const when = (value: string | null): string => (value ? formatRequestDate(value) : "");
