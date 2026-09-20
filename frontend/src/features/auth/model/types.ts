import type { UserRole } from "@/entities/user";

export type AuthMode = "login" | "register";

export type SubmitStatus = "idle" | "loading" | "error";

export type LoginFields = {
  email: string;
  password: string;
};

export type LoginFormState = {
  fields: LoginFields;
  status: SubmitStatus;
  error: string | null;
};

export type LoginFormAction =
  | { type: "field/change"; field: keyof LoginFields; value: string }
  | { type: "submit/start" }
  | { type: "submit/error"; message: string }
  | { type: "submit/done" };

export type RegisterFields = {
  fullName: string;
  email: string;
  phone: string;
  password: string;
};

export type RegisterFormState = {
  role: UserRole;
  fields: RegisterFields;
  status: SubmitStatus;
  error: string | null;
};

export type RegisterFormAction =
  | { type: "role/select"; role: UserRole }
  | { type: "field/change"; field: keyof RegisterFields; value: string }
  | { type: "submit/start" }
  | { type: "submit/error"; message: string }
  | { type: "submit/done" };
