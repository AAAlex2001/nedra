export type UserRole = "customer" | "expert";

export type User = {
  id: number;
  email: string;
  full_name: string;
  phone: string;
  role: UserRole;
  created_at: string;
};

export type CustomerRecord = {
  user_id: number;
  email: string;
  full_name: string;
  phone: string;
  created_at: string;
  company_name: string | null;
  company_inn: string | null;
  expertises_count: number;
};

export const ROLE_LABELS: Record<UserRole, string> = {
  customer: "Заказчик",
  expert: "Эксперт",
};
