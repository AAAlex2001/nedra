import {
  SECTION_TITLE,
  type ArticleAdminCard,
  type ArticleSection,
  type ArticleSort,
  type TagAdmin,
} from "@/entities/article";
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
  sort: ArticleSort;
  error: string | null;
};

const FILTERS: Array<ArticleSection | null> = [null, "blog", "news"];

const SORTS: ArticleSort[] = ["new", "views", "likes", "dislikes"];

const SORT_TITLE: Record<ArticleSort, string> = {
  new: "Новые",
  views: "Просмотры",
  likes: "Лайки",
  dislikes: "Дизлайки",
};

const AdminArticles = ({ basePath, articles, tags, section, sort, error }: AdminArticlesProps) => {
  const listPath = `${basePath}/articles`;

  const buildHref = (nextSection: ArticleSection | null, nextSort: ArticleSort) => {
    const params = new URLSearchParams();
    if (nextSection) params.set("section", nextSection);
    if (nextSort !== "new") params.set("sort", nextSort);

    const query = params.toString();
    if (!query) return listPath;

    return `${listPath}?${query}`;
  };

  let newHref = `${listPath}/new`;
  if (section) newHref = `${listPath}/new?section=${section}`;

  const sectionTabs = FILTERS.map((item) => ({
    key: item ?? "all",
    label: item ? SECTION_TITLE[item] : "Все",
    href: buildHref(item, sort),
  }));

  const sortTabs = SORTS.map((item) => ({
    key: item,
    label: SORT_TITLE[item],
    href: buildHref(section, item),
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

      <TabLinks items={sectionTabs} active={section ?? "all"} label="Раздел" stretch />
      <TabLinks items={sortTabs} active={sort} label="Сортировка" stretch />

      {error ? (
        <p className={styles.error}>{error}</p>
      ) : (
        <>
          <TagManager basePath={basePath} initialItems={tags} />
          <ArticlesTable
            key={`${section ?? "all"}-${sort}`}
            basePath={basePath}
            initialItems={articles}
          />
        </>
      )}
    </section>
  );
};

export default AdminArticles;
