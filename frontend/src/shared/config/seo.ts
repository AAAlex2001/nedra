import type { Metadata } from "next";
import { COMPANY_CONTACTS } from "./company";

/**
 * ВАЖНО: замените на реальный домен после деплоя.
 * От него зависят canonical-ссылки, sitemap, robots и Open Graph.
 */
export const SITE_URL = "https://npi-nedra.ru";

export const SITE_NAME = "НПИ «Недра»";
export const SITE_LEGAL_NAME =
  "ООО «Научный проектно-экспертный институт «Недра»";
export const SITE_DESCRIPTION =
  "Научный проектно-экспертный институт «Недра» — проектирование, инженерные изыскания, экологическая и промышленная экспертиза, научные исследования и сопровождение промышленных объектов в Новосибирске и по всей России.";

/** Картинка для Open Graph / соцсетей. Замените на брендовую 1200×630. */
export const OG_IMAGE = "/block_2.jpg";

export const SITE_KEYWORDS = [
  "НПИ Недра",
  "Недра Новосибирск",
  "научный проектно-экспертный институт",
  "проектный институт",
  "проектирование промышленных объектов",
  "проектно-сметная документация",
  "проектная документация",
  "инженерные изыскания",
  "экспертиза промышленной безопасности",
  "ЭПБ",
  "обоснование безопасности",
  "декларация промышленной безопасности",
  "промышленная безопасность",
  "аттестация по промышленной безопасности",
  "производственный контроль",
  "охрана труда",
  "специальная оценка условий труда",
  "СОУТ",
  "оценка профессиональных рисков",
  "обучение по охране труда",
  "система управления охраной труда",
  "техника безопасности",
  "пожарная безопасность",
  "техносферная безопасность",
  "экологическая экспертиза",
  "государственная экспертиза",
  "экспертиза проектной документации",
  "ОВОС",
  "оценка воздействия на окружающую среду",
  "инженерно-экологические изыскания",
  "научно-техническое сопровождение",
  "научно-техническое сопровождение строительства",
  "научно-испытательная лаборатория",
  "лабораторные исследования и испытания",
  "объекты культурного наследия",
  "реставрация памятников",
  "сохранение объектов культурного наследия",
  "научные исследования",
  "сопровождение промышленных объектов",
  "повышение квалификации",
  "дополнительное профессиональное образование",
  "обучение промышленная безопасность",
  "горное дело",
  "недропользование",
];

type PageSeo = {
  title: string;
  description: string;
};

/** Единый источник заголовков и описаний для всех страниц. */
export const PAGE_SEO: Record<string, PageSeo> = {
  "/": {
    title: "Проектирование, инженерные изыскания и экспертиза промышленных объектов",
    description: SITE_DESCRIPTION,
  },
  "/obshchestvennye-obsuzhdeniya": {
    title: "Общественные обсуждения",
    description:
      "Общественные обсуждения материалов оценки воздействия на окружающую среду (ОВОС) по проектам НПИ «Недра».",
  },
  "/politika-konfidencialnosti": {
    title: "Политика конфиденциальности",
    description:
      "Политика НПИ «Недра» в отношении обработки и защиты персональных данных пользователей сайта.",
  },
  "/svedeniya": {
    title: "Сведения об образовательной организации",
    description:
      "Официальный раздел «Сведения об образовательной организации» НПИ «Недра»: основные сведения, структура, документы, образование, руководство, платные услуги и другая обязательная информация.",
  },
  "/svedeniya/osnovnye-svedeniya": {
    title: "Основные сведения",
    description:
      "Основные сведения об образовательной организации НПИ «Недра»: полное наименование, дата создания, учредитель, адрес, режим работы, контакты и лицензия на образовательную деятельность.",
  },
  "/svedeniya/struktura-i-organy-upravleniya": {
    title: "Структура и органы управления образовательной организацией",
    description:
      "Структура и органы управления образовательной организации НПИ «Недра»: учредитель, директор, коллегиальные органы и контактная информация.",
  },
  "/svedeniya/dokumenty": {
    title: "Документы",
    description:
      "Официальные документы образовательной организации НПИ «Недра»: устав, лицензия, локальные нормативные акты, положения и приказы.",
  },
  "/svedeniya/obrazovanie": {
    title: "Образование",
    description:
      "Информация об образовательной деятельности НПИ «Недра»: реализуемые программы повышения квалификации, документы об образовании и учебные материалы.",
  },
  "/svedeniya/rukovodstvo": {
    title: "Руководство",
    description:
      "Руководство образовательной организации НПИ «Недра»: сведения о директоре и контактные данные для связи по вопросам образовательной деятельности.",
  },
  "/svedeniya/pedagogicheskiy-sostav": {
    title: "Педагогический состав",
    description:
      "Педагогический (научно-педагогический) состав образовательной организации НПИ «Недра»: преподаватели, квалификация и документы о повышении квалификации.",
  },
  "/svedeniya/materialno-tehnicheskoe-obespechenie": {
    title:
      "Материально-техническое обеспечение и оснащённость образовательного процесса",
    description:
      "Материально-техническое обеспечение и оснащённость образовательного процесса НПИ «Недра», доступная среда и условия обучения, в том числе для лиц с ОВЗ.",
  },
  "/svedeniya/platnye-obrazovatelnye-uslugi": {
    title: "Платные образовательные услуги",
    description:
      "Платные образовательные услуги НПИ «Недра»: порядок предоставления, стоимость обучения и документы, регламентирующие оказание платных услуг.",
  },
  "/svedeniya/finansovo-hozyaystvennaya-deyatelnost": {
    title: "Финансово-хозяйственная деятельность",
    description:
      "Финансово-хозяйственная деятельность образовательной организации НПИ «Недра»: источники финансирования образовательной деятельности и обеспечение прозрачности.",
  },
  "/svedeniya/vakantnye-mesta": {
    title: "Вакантные места для приёма (перевода) обучающихся",
    description:
      "Вакантные места для приёма и перевода обучающихся в НПИ «Недра» по источникам финансирования на текущий год.",
  },
  "/svedeniya/stipendii-i-mery-podderzhki": {
    title: "Стипендии и меры поддержки обучающихся",
    description:
      "Информация о стипендиях и мерах социальной поддержки обучающихся в образовательной организации НПИ «Недра».",
  },
  "/svedeniya/mezhdunarodnoe-sotrudnichestvo": {
    title: "Международное сотрудничество",
    description:
      "Международное сотрудничество образовательной организации НПИ «Недра»: договоры с иностранными организациями и международная аккредитация образовательных программ.",
  },
  "/svedeniya/organizatsiya-pitaniya": {
    title: "Организация питания в образовательной организации",
    description:
      "Информация об организации питания обучающихся в образовательной организации НПИ «Недра».",
  },
};

/** Единый билдер метаданных страницы: title, description, canonical, OG, Twitter. */
export function buildMetadata(path: string): Metadata {
  const page = PAGE_SEO[path];

  if (!page) {
    return { alternates: { canonical: path } };
  }

  const url = `${SITE_URL}${path}`;
  const ogTitle = `${page.title} | ${SITE_NAME}`;

  return {
    title: page.title,
    description: page.description,
    alternates: { canonical: url },
    openGraph: {
      type: "website",
      url,
      siteName: SITE_NAME,
      locale: "ru_RU",
      title: ogTitle,
      description: page.description,
      images: [{ url: OG_IMAGE, width: 1200, height: 630, alt: SITE_NAME }],
    },
    twitter: {
      card: "summary_large_image",
      title: ogTitle,
      description: page.description,
      images: [OG_IMAGE],
    },
  };
}

/** JSON-LD: организация (для сниппетов и графа знаний). */
export const organizationJsonLd = {
  "@context": "https://schema.org",
  "@type": "Organization",
  name: SITE_LEGAL_NAME,
  alternateName: SITE_NAME,
  url: SITE_URL,
  logo: `${SITE_URL}/logo.svg`,
  image: `${SITE_URL}${OG_IMAGE}`,
  description: SITE_DESCRIPTION,
  email: COMPANY_CONTACTS.email,
  telephone: `+${COMPANY_CONTACTS.phoneHref}`,
  address: {
    "@type": "PostalAddress",
    postalCode: "630008",
    addressRegion: "Новосибирская область",
    addressLocality: "Новосибирск",
    streetAddress: "ул. Кирова, зд. 113/2, помещ. 2409",
    addressCountry: "RU",
  },
  contactPoint: {
    "@type": "ContactPoint",
    telephone: COMPANY_CONTACTS.phoneHref,
    email: COMPANY_CONTACTS.email,
    contactType: "customer service",
    areaServed: "RU",
    availableLanguage: "Russian",
  },
  openingHoursSpecification: {
    "@type": "OpeningHoursSpecification",
    dayOfWeek: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    opens: "08:30",
    closes: "17:00",
  },
};

/** JSON-LD: сайт. */
export const websiteJsonLd = {
  "@context": "https://schema.org",
  "@type": "WebSite",
  name: SITE_NAME,
  alternateName: SITE_LEGAL_NAME,
  url: SITE_URL,
  inLanguage: "ru-RU",
};
