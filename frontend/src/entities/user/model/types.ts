export type UserRole = "customer" | "expert";

export type User = {
  id: number;
  email: string;
  full_name: string;
  phone: string;
  role: UserRole;
  is_expert: boolean;
  created_at: string;
};

export const ROLE_LABELS: Record<UserRole, string> = {
  customer: "Заказчик",
  expert: "Эксперт",
};
