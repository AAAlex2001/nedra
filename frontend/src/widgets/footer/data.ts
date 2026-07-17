import { SVEDENIYA_BASE, SVEDENIYA_SECTIONS } from "@/shared/ui/svedeniya-nav/data";

export type FooterLink = {
  label: string;
  href: string;
};

export type FooterLinkGroup = {
  title: string;
  wide?: boolean;
  links: FooterLink[];
};

export const FOOTER_DATA = {
  company: "ООО НПИ «Недра»",
  description:
    "Научно-производственный институт, выполняющий проектирование, инженерные изыскания, экспертизу, научные исследования и сопровождение промышленных объектов.",
  contactsTitle: "Контакты",
  sitemapTitle: "Карта сайта",
  copyright: "© 2026 ООО НПИ «Недра». Все права защищены.",
  privacy: { label: "Политика конфиденциальности", href: "#" },
};

export const FOOTER_SITEMAP: FooterLinkGroup[] = [
  {
    title: "Сайт",
    links: [
      { label: "Главная", href: "/" },
      { label: "О нас", href: "/#about" },
      { label: "Направления деятельности", href: "/#directions" },
      { label: "Услуги", href: "/#services" },
      { label: "Лаборатория", href: "/#laboratory" },
      { label: "Разрешительные документы", href: "/#documents" },
      { label: "Партнёры", href: "/#partners" },
      { label: "Общественные обсуждения", href: "/obshchestvennye-obsuzhdeniya" },
      { label: "Контакты", href: "/#contacts" },
    ],
  },
  {
    title: "Сведения об образовательной организации",
    wide: true,
    links: [
      { label: "Сведения об образовательной организации", href: SVEDENIYA_BASE },
      ...SVEDENIYA_SECTIONS.map((section) => ({
        label: section.label,
        href: `${SVEDENIYA_BASE}/${section.slug}`,
      })),
    ],
  },
];
