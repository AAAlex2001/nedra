export type RequestRecord = {
  request_id: number;
  name: string;
  telephone: string;
  email: string;
  activity: number;
  direction: number;
  company_name: string | null;
  inn: string | null;
  comment: string;
  created_at: string;
};
