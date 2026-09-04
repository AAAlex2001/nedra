export type ServiceDoc = {
  title: string;
  meta: string;
  href: string;
};

export type LicenseColumn = {
  text?: string;
  doc?: ServiceDoc;
};

export type Licenses = {
  title?: string;
  note?: string;
  columns: LicenseColumn[];
};

export type DetailSection = {
  title: string;
  text?: string;
  bullets?: string[];
  trailing?: string;
};

export type Contact = {
  phone: string;
  email?: string;
  person: string;
};

export type SubService = {
  id: string;
  label: string;
  sections: DetailSection[];
  contact: Contact;
  licenses?: Licenses;
};

export type Direction = {
  id: string;
  title: string;
  serviceCount: number;
  image: string;
  heroTitle: string;
  summary: string;
  services: SubService[];
};
