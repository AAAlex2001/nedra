import { ArticlesPanel, type ArticleCardData } from "@/entities/article";
import type { AuditChecklistItem } from "@/entities/expertise";
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
import AuditPrice from "./ui/audit-price";
import ChecklistPreview from "./ui/checklist-preview";
import styles from "./style.module.scss";

type BlitsAuditLandingProps = {
  checklist: AuditChecklistItem[];
  price: string | null;
  articles: ArticleCardData[];
};

const PAGE_PATH = "/blits-audit";

const START_TEXT = "Загрузить документы";

const JSON_LD = [
  buildBreadcrumbsJsonLd([
    { name: "Главная", path: "/" },
    { name: "Блиц-аудит", path: PAGE_PATH },
  ]),
  buildServiceJsonLd({
    name: PAGE_SEO[PAGE_PATH].title,
    description: PAGE_SEO[PAGE_PATH].description,
    path: PAGE_PATH,
    prices: [],
    serviceType: "Аудит системы управления промышленной безопасностью",
  }),
  buildFaqJsonLd(FAQ_ITEMS),
];

const BlitsAuditLanding = ({ checklist, price, articles }: BlitsAuditLandingProps) => (
  <main className={`${styles.page} theme-green`}>
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(JSON_LD) }}
    />

    <Breadcrumbs
      items={[
        { label: "Главная", href: "/" },
        { label: "Блиц-аудит" },
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
            secondaryHref="#perechen"
            secondaryText="Перечень документов"
          />
        }
      />

      {checklist.length > 0 && <ChecklistPreview checklist={checklist} />}

      <LandingFeatures title="Аудит без выезда и долгих согласований" items={FEATURES} />

      <AuditPrice price={price} startText={START_TEXT} />

      <LandingSteps
        id="kak-prohodit"
        title="Как проходит аудит"
        lead="Девять шагов от загрузки документов до акта выполненных работ."
        imagePrefix="Аудит системы управления промышленной безопасностью"
        steps={STEPS}
      />

      {articles.length > 0 && (
        <ArticlesPanel
          title="Разбираем СУПБ и производственный контроль"
          lead="Кому обязательна система управления, как её внедрить и что проверяет Ростехнадзор."
          items={articles}
        />
      )}

      <Faq items={FAQ_ITEMS} title="Частые вопросы" />

      <LandingCta
        badge="Аудит СУПБ онлайн"
        title="Проверьте систему управления промбезопасностью до инспектора"
        points={CTA_POINTS}
        image="/audit/13.webp"
        imageAlt="Документы системы управления промышленной безопасностью, чек-лист аудита и отчёт с электронной подписью"
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

export default BlitsAuditLanding;
