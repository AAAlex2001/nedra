export type Attestation = {
  area_code: string;
  object_code: string;
  category: number;
};

export type CommissionApplicationRecord = {
  id: number;
  full_name: string;
  phone: string;
  email: string;
  attestations: Attestation[];
  created_at: string;
};
