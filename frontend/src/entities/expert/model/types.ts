export type Direction = {
  code: string;
  title: string;
};

export type ExpertiseObject = {
  code: string;
  label: string;
  title: string;
};

export type AttestationArea = {
  code: string;
  title: string;
  objects: string[];
};

export type ExpertCatalog = {
  directions: Direction[];
  areas: AttestationArea[];
  objects: ExpertiseObject[];
  categories: number[];
};

export type Certificate = {
  id: number;
  area_code: string;
  object_code: string;
  category: number;
  valid_until: string;
  scan_name: string | null;
};

export type ExpertProfile = {
  directions: string[];
  approved_at: string;
  certificates: Certificate[];
};

export type ApplicationStatus = "pending" | "approved" | "rejected";

export type ExpertApplicationRecord = {
  id: number;
  email: string;
  full_name: string;
  phone: string;
  directions: string[];
  status: ApplicationStatus;
  admin_comment: string | null;
  created_at: string;
  reviewed_at: string | null;
  certificates: Certificate[];
};

export const APPLICATION_STATUS_LABELS: Record<ApplicationStatus, string> = {
  pending: "На проверке",
  approved: "Одобрена",
  rejected: "Отклонена",
};
