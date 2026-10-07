export type LegalListBlock = {
  type: "list";
  intro: string;
  marker: "dash" | "bullet";
  items: string[];
};

export type LegalDetailsBlock = {
  type: "details";
  items: Array<{
    label: string;
    values: string[];
    list?: boolean;
  }>;
};

export type LegalBlock =
  | { type: "paragraph"; text: string }
  | LegalListBlock
  | LegalDetailsBlock;

export type LegalSection = {
  number: string;
  title?: string;
  blocks: LegalBlock[];
};

export type LegalDocument = {
  title: string;
  intro?: string[];
  sections: LegalSection[];
};
