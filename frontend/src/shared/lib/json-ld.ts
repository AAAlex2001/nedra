import { SITE_LEGAL_NAME, SITE_NAME, SITE_URL } from "@/shared/config/seo";
import type { FaqItem } from "@/shared/ui/faq";

/** Разметка FAQPage: Яндекс и Google показывают такие вопросы прямо в выдаче. */
export const buildFaqJsonLd = (items: FaqItem[]) => ({
  "@context": "https://schema.org",
  "@type": "FAQPage",
  mainEntity: items.map((item) => ({
    "@type": "Question",
    name: item.question,
    acceptedAnswer: { "@type": "Answer", text: item.answer },
  })),
});

export type BreadcrumbEntry = {
  name: string;
  path?: string;
};

/** Разметка BreadcrumbList: цепочка навигации в сниппете вместо голого URL. */
export const buildBreadcrumbsJsonLd = (items: BreadcrumbEntry[]) => ({
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  itemListElement: items.map((item, index) => ({
    "@type": "ListItem",
    position: index + 1,
    name: item.name,
    ...(item.path ? { item: `${SITE_URL}${item.path}` } : {}),
  })),
});

type ServiceParams = {
  name: string;
  description: string;
  path: string;
  prices: number[];
};

/** Разметка Service с вилкой цен: даёт в выдаче блок услуги и стоимость. */
export const buildServiceJsonLd = ({ name, description, path, prices }: ServiceParams) => {
  const offers =
    prices.length === 0
      ? {}
      : {
          offers: {
            "@type": "AggregateOffer",
            priceCurrency: "RUB",
            lowPrice: Math.min(...prices),
            highPrice: Math.max(...prices),
            offerCount: prices.length,
          },
        };

  return {
    "@context": "https://schema.org",
    "@type": "Service",
    name,
    description,
    serviceType: "Экспертиза промышленной безопасности",
    url: `${SITE_URL}${path}`,
    areaServed: { "@type": "Country", name: "Россия" },
    provider: {
      "@type": "Organization",
      name: SITE_LEGAL_NAME,
      alternateName: SITE_NAME,
      url: SITE_URL,
    },
    ...offers,
  };
};
