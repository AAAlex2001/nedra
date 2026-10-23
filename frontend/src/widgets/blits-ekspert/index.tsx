import { ArticlesPanel, type ArticleCardData } from "@/entities/article";
import type { ExpertCatalog } from "@/entities/expert";
import type { Tariff } from "@/entities/tariff";
import { StartButtons, StickyStart } from "@/features/auth";
import { PAGE_SEO } from "@/shared/config/seo";
import { buildBreadcrumbsJsonLd, buildFaqJsonLd, buildServiceJsonLd } from "@/shared/lib/json-ld";
import Breadcrumbs from "@/shared/ui/breadcrumbs";
import Faq from "@/shared/ui/faq";
import LandingCta from "@/shared/ui/landing-cta";
import LandingFeatures from "@/shared/ui/landing-features";
import LandingHero from "@/shared/ui/landing-hero";
import LandingSteps from "@/shared/ui/landing-steps";
import {
  ARTICLE_SLUGS,
  CTA_DECOR,
  CTA_POINTS,
  FAQ_ITEMS,
  FEATURES,
  HERO,
  SLIDES,
  STEPS,
} from "./data";
import AreasList from "./ui/areas-list";
import Calculator from "./ui/calculator";
import ObjectsTiles from "./ui/objects-tiles";
import styles from "./style.module.scss";

type BlitsEkspertLandingProps = {
  catalog: ExpertCatalog | null;
  tariffs: Tariff[];
  articles: ArticleCardData[];
};

const PAGE_PATH = "/blits-ekspert";

const START_TEXT = "Отправить документацию";

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
      <LandingHero
        title={HERO.title}
        text={HERO.text}
        slides={SLIDES}
        action={
          <StartButtons
            text={START_TEXT}
            secondaryHref="#stoimost"
            secondaryText="Узнать стоимость"
          />
        }
      />

      {catalog && <ObjectsTiles catalog={catalog} />}

      {catalog && <Calculator catalog={catalog} tariffs={tariffs} />}

      <LandingFeatures title="Экспертиза без переписки и ожидания" items={FEATURES} />

      <LandingSteps
        id="kak-prohodit"
        title="Как проходит экспертиза"
        lead="Девять шагов от загрузки документации до акта выполненных работ."
        imagePrefix="Экспертиза промышленной безопасности"
        steps={STEPS}
      />

      {catalog && <AreasList catalog={catalog} />}

      {articles.length > 0 && (
        <ArticlesPanel
          title="Разбираем экспертизу по шагам"
          lead="Сроки, штрафы, документы и требования Ростехнадзора — без канцелярита, со ссылками на первоисточники."
          items={articles}
        />
      )}

      <Faq items={FAQ_ITEMS} title="Частые вопросы" />

      <LandingCta
        badge="Экспертиза от 1 дня"
        title="Отправьте документацию на экспертизу"
        points={CTA_POINTS}
        image="/blitz/18.webp"
        imageAlt="Документация, заключение с электронной подписью и технические устройства опасного производственного объекта"
        decor={CTA_DECOR}
        action={
          <StartButtons
            text={START_TEXT}
            secondaryHref="#kak-prohodit"
            secondaryText="Как это работает"
          />
        }
      />
    </div>

    <StickyStart text={START_TEXT} />
  </main>
);

export { ARTICLE_SLUGS };

export default BlitsEkspertLanding;
