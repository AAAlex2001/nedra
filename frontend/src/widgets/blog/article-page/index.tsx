import Image from "next/image";
import Link from "next/link";
import type { ReactNode } from "react";
import {
  ARTICLE_COVER_SIZES,
  SECTION_PATH,
  buildArticleJsonLd,
  buildFaqJsonLd,
  isOptimizableCover,
  splitContent,
  type Article,
} from "@/entities/article";
import { ReactionBar } from "@/features/article-reactions";
import { formatDate } from "@/shared/lib/date";
import ShareButton from "@/shared/ui/share-button";
import styles from "./style.module.scss";

type ArticlePageProps = {
  article: Article;
  middle?: ReactNode;
};

const ArticlePage = ({ article, middle }: ArticlePageProps) => {
  const sectionPath = SECTION_PATH[article.section];
  const [firstPart, secondPart] = middle ? splitContent(article) : [article.content, ""];

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
        {article.toc.length > 0 && (
          <aside className={styles.aside}>
            <nav className={styles.toc} aria-label="Оглавление">
              <p className={styles.tocTitle}>Оглавление</p>
              <ol className={styles.tocList}>
                {article.toc.map((item, index) => (
                  <li key={item.id}>
                    <a href={`#${item.id}`} className={styles.tocLink}>
                      <span className={styles.tocNumber}>
                        {String(index + 1).padStart(2, "0")}
                      </span>
                      {item.title}
                    </a>
                  </li>
                ))}
              </ol>
            </nav>
          </aside>
        )}

        <div className={styles.main}>
          <div
            className={styles.content}
            dangerouslySetInnerHTML={{ __html: firstPart }}
          />
        </div>
      </div>

      {middle && <div className={styles.middle}>{middle}</div>}

      <div className={styles.layout}>
        {article.toc.length > 0 && <div className={styles.asideSpacer} />}

        <div className={styles.main}>
          {secondPart && (
            <div
              className={styles.content}
              dangerouslySetInnerHTML={{ __html: secondPart }}
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
