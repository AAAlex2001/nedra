import { SECTION_TITLE, type ArticleAdminCard, type ArticleSection, type TagAdmin } from "@/entities/article";
import { ArticlesTable, TagManager } from "@/features/articles-admin";
import AccentLine from "@/shared/ui/accent-line";
import OutlineButton from "@/shared/ui/outline-button";
import { TabLinks } from "@/shared/ui/tabs";
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

  const tabs = FILTERS.map((item) => ({
    key: item ?? "all",
    label: item ? SECTION_TITLE[item] : "Все",
    href: item ? `${listPath}?section=${item}` : listPath,
  }));

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

      <TabLinks items={tabs} active={section ?? "all"} label="Раздел" />

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
