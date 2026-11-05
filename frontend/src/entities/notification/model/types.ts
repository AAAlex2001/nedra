export type Notification = {
  id: number;
  expertise_id: number | null;
  audit_id: number | null;
  kind: string | null;
  text: string;
  created_at: string;
  read_at: string | null;
};
