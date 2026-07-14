export type SvedeniyaSection = {
  slug: string;
  label: string;
};

export const SVEDENIYA_BASE = "/svedeniya";

export const SVEDENIYA_SECTIONS: SvedeniyaSection[] = [
  { slug: "osnovnye-svedeniya", label: "Основные сведения" },
  {
    slug: "struktura-i-organy-upravleniya",
    label: "Структура и органы управления образовательной организацией",
  },
  { slug: "dokumenty", label: "Документы" },
  { slug: "obrazovanie", label: "Образование" },
  { slug: "rukovodstvo", label: "Руководство" },
  { slug: "pedagogicheskiy-sostav", label: "Педагогический состав" },
  {
    slug: "materialno-tehnicheskoe-obespechenie",
    label: "Материально-техническое обеспечение и оснащённость образовательного процесса. Доступная среда",
  },
  {
    slug: "platnye-obrazovatelnye-uslugi",
    label: "Платные образовательные услуги",
  },
  {
    slug: "finansovo-hozyaystvennaya-deyatelnost",
    label: "Финансово-хозяйственная деятельность",
  },
  {
    slug: "vakantnye-mesta",
    label: "Вакантные места для приема (перевода) обучающихся",
  },
  {
    slug: "stipendii-i-mery-podderzhki",
    label: "Стипендии и меры поддержки обучающихся",
  },
  {
    slug: "mezhdunarodnoe-sotrudnichestvo",
    label: "Международное сотрудничество",
  },
  {
    slug: "organizatsiya-pitaniya",
    label: "Организация питания в образовательной организации",
  },
];
