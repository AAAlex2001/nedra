import { postJson } from "@/shared/api";
import type { RequestFields } from "../model/types";

export type CreatedRequest = {
  request_id: number;
  direction: number;
  created_at: string;
};

/** Приведение полей формы к контракту RequestInSchema на бэкенде. */
export const createRequest = (fields: RequestFields, activity: number) =>
  postJson<CreatedRequest>("/v1/request", {
    name: fields.name.trim(),
    telephone: fields.telephone.trim(),
    email: fields.email.trim(),
    activity,
    company_name: fields.companyName.trim() || null,
    inn: fields.inn.trim() || null,
    comment: fields.comment.trim(),
  });
