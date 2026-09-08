import Link from "next/link";
import {
  ARTICLES_PER_PAGE,
  ArticleCard,
  type ArticleList,
  type Tag,
} from "@/entities/article";
import styles from "./style.module.scss";

type ArticlesListProps = {
  list: ArticleList;
  tags: Tag[];
  activeTag: string | null;
  page: number;
};

const buildHref = (tag: string | null, page: number) => {
  const params = new URLSearchParams();
  if (tag) params.set("tag", tag);
  if (page > 1) params.set("page", String(page));

  const query = params.toString();
  return query ? `/blog?${query}` : "/blog";
};

const ArticlesList = ({ list, tags, activeTag, page }: ArticlesListProps) => {
  const totalPages = Math.max(1, Math.ceil(list.total / ARTICLES_PER_PAGE));
  const pages = Array.from({ length: totalPages }, (_, index) => index + 1);

  return (
    <div className={styles.root}>
      <nav className={styles.filters} aria-label="Фильтр по тегам">
        <Link
          href="/blog"
          className={`${styles.pill} ${activeTag ? "" : styles.pillActive}`}
        >
          Все
        </Link>
        {tags.map((tag) => (
          <Link
            key={tag.slug}
            href={buildHref(tag.slug, 1)}
            className={`${styles.pill} ${activeTag === tag.slug ? styles.pillActive : ""}`}
          >
            {tag.title}
          </Link>
        ))}
      </nav>

      {list.articles.length === 0 ? (
        <p className={styles.empty}>Статей пока нет.</p>
      ) : (
        <ul className={styles.grid}>
          {list.articles.map((article) => (
            <li key={article.slug} className={styles.cell}>
              <ArticleCard article={article} />
            </li>
          ))}
        </ul>
      )}

      {totalPages > 1 && (
        <nav className={styles.pagination} aria-label="Страницы">
          {page > 1 && (
            <Link href={buildHref(activeTag, page - 1)} className={styles.pageArrow}>
              ← Назад
            </Link>
          )}

          {pages.map((number) => (
            <Link
              key={number}
              href={buildHref(activeTag, number)}
              className={`${styles.pageNumber} ${number === page ? styles.pageActive : ""}`}
              aria-current={number === page ? "page" : undefined}
            >
              {number}
            </Link>
          ))}

          {page < totalPages && (
            <Link href={buildHref(activeTag, page + 1)} className={styles.pageArrow}>
              Вперёд →
            </Link>
          )}
        </nav>
      )}
    </div>
  );
};

export default ArticlesList;
