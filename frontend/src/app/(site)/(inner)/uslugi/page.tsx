import { DIRECTIONS } from "@/entities/service";
import { buildMetadata, SITE_NAME, SITE_URL } from "@/shared/config/seo";
import { buildFaqJsonLd } from "@/shared/lib/json-ld";
import Services from "@/widgets/services";
import { SERVICES_FAQ } from "@/widgets/services/data";

export const metadata = buildMetadata("/uslugi");

const catalog = {
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "@id": `${SITE_URL}/uslugi#page`,
  name: `Услуги ${SITE_NAME}`,
  url: `${SITE_URL}/uslugi`,
  inLanguage: "ru-RU",
  description:
    "Проектирование, инженерные изыскания, экспертиза промышленной безопасности, аудит, исследования и обучение. Задачи заказчика, состав работ и результаты услуг НПИ «Недра».",
  mainEntity: {
    "@type": "OfferCatalog",
    name: "Услуги института",
    itemListElement: DIRECTIONS.map(direction => ({
      "@type": "OfferCatalog",
      name: direction.title,
      itemListElement: direction.services.map(service => ({
        "@type": "Offer",
        itemOffered: {
          "@type": "Service",
          name: service.label,
          url: `${SITE_URL}/uslugi#service-${service.id}`,
          description:
            service.sections.find(section => section.title === "Описание услуги")?.text ||
            service.sections.find(section => section.title === "Описание услуги")?.bullets?.join(" ") ||
            direction.summary,
          provider: {
            "@type": "Organization",
            name: SITE_NAME,
            url: SITE_URL,
          },
        },
      })),
    })),
  },
};

export default function ServicesPage() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(catalog).replace(/</g, "\\u003c"),
        }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(buildFaqJsonLd(SERVICES_FAQ)).replace(/</g, "\\u003c"),
        }}
      />
      <Services />
    </>
  );
}
