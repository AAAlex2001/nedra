import Link from "next/link";
import { SECTION_TITLE, type ArticleAdminCard, type ArticleSection, type TagAdmin } from "@/entities/article";
import { ArticlesTable, TagManager } from "@/features/articles-admin";
import AccentLine from "@/shared/ui/accent-line";
import OutlineButton from "@/shared/ui/outline-button";
import styles from "./style.module.scss";

type AdminArticlesProps = {
  basePath: string;
  articles: ArticleAdminCard[];
  tags: TagAdmin[];
  section: ArticleSection | null;
  error: string | null;
};

const FILTERS: Array<ArticleSection | null> = [null, "blog", "news"];

const AdminArticles = ({ basePath, articles, tags, section, error }: AdminArticlesProps) => {
  const listPath = `${basePath}/articles`;

  let newHref = `${listPath}/new`;
  if (section) newHref = `${listPath}/new?section=${section}`;

  return (
    <section className={styles.section}>
      <div className={styles.head}>
        <div className={styles.heading}>
          <h1 className={styles.title}>Статьи</h1>
          <AccentLine width={30} />
          <p className={styles.subtitle}>
            {articles.length > 0
              ? `Всего статей: ${articles.length}`
              : "Здесь появятся статьи, когда вы их добавите"}
          </p>
        </div>

        <OutlineButton href={newHref}>Новая статья</OutlineButton>
      </div>

      <nav className={styles.filters} aria-label="Раздел">
        {FILTERS.map((item) => (
          <Link
            key={item ?? "all"}
            href={item ? `${listPath}?section=${item}` : listPath}
            className={`${styles.pill} ${item === section ? styles.pillActive : ""}`}
          >
            {item ? SECTION_TITLE[item] : "Все"}
          </Link>
        ))}
      </nav>

      {error ? (
        <p className={styles.error}>{error}</p>
      ) : (
        <>
          <TagManager basePath={basePath} initialItems={tags} />
          <ArticlesTable key={section ?? "all"} basePath={basePath} initialItems={articles} />
        </>
      )}
    </section>
  );
};

export default AdminArticles;
