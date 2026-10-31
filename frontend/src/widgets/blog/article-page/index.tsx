import Image from "next/image";
import Link from "next/link";
import type { ReactNode } from "react";
import {
  ARTICLE_COVER_SIZES,
  SECTION_PATH,
  buildArticleJsonLd,
  buildFaqJsonLd,
  isOptimizableCover,
  splitAtHeadings,
  type Article,
} from "@/entities/article";
import { ReactionBar } from "@/features/article-reactions";
import { formatDate } from "@/shared/lib/date";
import ShareButton from "@/shared/ui/share-button";
import ArticleToc from "./ui/article-toc";
import RequestWidget from "./ui/request-widget";
import StickyAside from "./ui/sticky-aside";
import styles from "./style.module.scss";

type ArticlePageProps = {
  article: Article;
  promo?: ReactNode;
  middle?: ReactNode;
};

const ArticlePage = ({ article, promo, middle }: ArticlePageProps) => {
  const sectionPath = SECTION_PATH[article.section];
  const [beforePromo, betweenBlocks, afterServices] = splitAtHeadings(article.content, [1, 3]);

  const hasToc = article.toc.length > 0;
  const jsonLd = buildArticleJsonLd(article);
  const faqJsonLd = buildFaqJsonLd(article);

  const initialStats = {
    views_count: article.views_count,
    likes_count: article.likes_count,
    dislikes_count: article.dislikes_count,
    my_reaction: null,
  };

  return (
    <article className={styles.article}>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      {faqJsonLd && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(faqJsonLd) }}
        />
      )}

      <header className={styles.header}>
        <h1 className={styles.title}>{article.title}</h1>

        {article.description && <p className={styles.lead}>{article.description}</p>}

        <div className={styles.meta}>
          {article.tags.map((tag) => (
            <Link key={tag.slug} href={`${sectionPath}?tag=${tag.slug}`} className={styles.tag}>
              {tag.title}
            </Link>
          ))}
          <time className={styles.date} dateTime={article.published_at ?? undefined}>
            {formatDate(article.published_at)}
          </time>
        </div>
      </header>

      <div className={styles.layout}>
        <StickyAside className={styles.widget}>
          <RequestWidget />
        </StickyAside>

        <div className={styles.main} data-article-main>
          {hasToc && (
            <div className={styles.inlineToc}>
              <ArticleToc items={article.toc} variant="collapsible" />
            </div>
          )}

          {hasToc && <ArticleToc items={article.toc} variant="floating" />}

          <div
            className={styles.content}
            dangerouslySetInnerHTML={{ __html: beforePromo }}
          />

          {promo}

          {betweenBlocks && (
            <div
              className={styles.content}
              dangerouslySetInnerHTML={{ __html: betweenBlocks }}
            />
          )}

          {middle}

          {afterServices && (
            <div
              className={styles.content}
              dangerouslySetInnerHTML={{ __html: afterServices }}
            />
          )}

          {article.cover_image && (
            <div className={styles.cover}>
              <Image
                src={article.cover_image}
                alt={article.title}
                fill
                sizes={ARTICLE_COVER_SIZES}
                unoptimized={!isOptimizableCover(article.cover_image)}
                className={styles.coverImage}
              />
            </div>
          )}

          <div className={styles.actions}>
            <ShareButton />
          </div>

          <ReactionBar slug={article.slug} initial={initialStats} />
        </div>
      </div>
    </article>
  );
};

export default ArticlePage;
