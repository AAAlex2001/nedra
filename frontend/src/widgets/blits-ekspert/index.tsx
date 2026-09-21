import type { ArticleCardData } from "@/entities/article";
import type { ExpertCatalog } from "@/entities/expert";
import type { Tariff } from "@/entities/tariff";
import { PAGE_SEO } from "@/shared/config/seo";
import { buildBreadcrumbsJsonLd, buildFaqJsonLd, buildServiceJsonLd } from "@/shared/lib/json-ld";
import Breadcrumbs from "@/shared/ui/breadcrumbs";
import Faq from "@/shared/ui/faq";
import { ARTICLE_SLUGS, FAQ_ITEMS } from "./data";
import AreasList from "./ui/areas-list";
import Articles from "./ui/articles";
import Calculator from "./ui/calculator";
import Cta from "./ui/cta";
import Features from "./ui/features";
import Flow from "./ui/flow";
import Hero from "./ui/hero";
import ObjectsTiles from "./ui/objects-tiles";
import StartButtons from "./ui/start-buttons";
import StickyCta from "./ui/sticky-cta";
import styles from "./style.module.scss";

type BlitsEkspertLandingProps = {
  catalog: ExpertCatalog | null;
  tariffs: Tariff[];
  articles: ArticleCardData[];
};

const PAGE_PATH = "/blits-ekspert";

const buildJsonLd = (tariffs: Tariff[]) => [
  buildBreadcrumbsJsonLd([
    { name: "Главная", path: "/" },
    { name: "Блиц-эксперт", path: PAGE_PATH },
  ]),
  buildServiceJsonLd({
    name: PAGE_SEO[PAGE_PATH].title,
    description: PAGE_SEO[PAGE_PATH].description,
    path: PAGE_PATH,
    prices: tariffs.map((item) => Number(item.price)).filter((price) => price > 0),
  }),
  buildFaqJsonLd(FAQ_ITEMS),
];

const BlitsEkspertLanding = ({ catalog, tariffs, articles }: BlitsEkspertLandingProps) => (
  <main className={styles.page}>
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(buildJsonLd(tariffs)) }}
    />

    <Breadcrumbs
      items={[
        { label: "Главная", href: "/" },
        { label: "Блиц-эксперт" },
      ]}
    />

    <div className={styles.inner}>
      <Hero action={<StartButtons secondaryHref="#stoimost" secondaryText="Узнать стоимость" />} />

      {catalog && <ObjectsTiles catalog={catalog} />}

      {catalog && <Calculator catalog={catalog} tariffs={tariffs} />}

      <Features />

      <Flow />

      {catalog && <AreasList catalog={catalog} />}

      {articles.length > 0 && <Articles items={articles} />}

      <Faq items={FAQ_ITEMS} title="Частые вопросы" />

      <Cta />
    </div>

    <StickyCta />
  </main>
);

export { ARTICLE_SLUGS };

export default BlitsEkspertLanding;
