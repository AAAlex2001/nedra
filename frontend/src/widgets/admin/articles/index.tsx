import type { ArticleAdminCard, TagAdmin } from "@/entities/article";
import { ArticlesTable, TagManager } from "@/features/articles-admin";
import AccentLine from "@/shared/ui/accent-line";
import OutlineButton from "@/shared/ui/outline-button";
import styles from "./style.module.scss";

type AdminArticlesProps = {
  basePath: string;
  articles: ArticleAdminCard[];
  tags: TagAdmin[];
  error: string | null;
};

const AdminArticles = ({ basePath, articles, tags, error }: AdminArticlesProps) => {
  return (
    <section className={styles.section}>
      <div className={styles.head}>
        <div className={styles.heading}>
          <h1 className={styles.title}>Статьи блога</h1>
          <AccentLine width={30} />
          <p className={styles.subtitle}>
            {articles.length > 0
              ? `Всего статей: ${articles.length}`
              : "Здесь появятся статьи, когда вы их добавите"}
          </p>
        </div>

        <OutlineButton href={`${basePath}/articles/new`}>Новая статья</OutlineButton>
      </div>

      {error ? (
        <p className={styles.error}>{error}</p>
      ) : (
        <>
          <TagManager basePath={basePath} initialItems={tags} />
          <ArticlesTable basePath={basePath} initialItems={articles} />
        </>
      )}
    </section>
  );
};

export default AdminArticles;
