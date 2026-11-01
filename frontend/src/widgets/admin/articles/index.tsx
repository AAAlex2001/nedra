import {
  SECTION_TITLE,
  type ArticleAdminList,
  type ArticleSection,
  type ArticleSort,
  type TagAdmin,
} from "@/entities/article";
import {
  ArticlesSearch,
  ArticlesTable,
  TagManager,
  buildAdminListHref,
  type AdminListFilters,
} from "@/features/articles-admin";
import AccentLine from "@/shared/ui/accent-line";
import OutlineButton from "@/shared/ui/outline-button";
import { TabLinks } from "@/shared/ui/tabs";
import styles from "./style.module.scss";

type AdminArticlesProps = {
  basePath: string;
  list: ArticleAdminList;
  tags: TagAdmin[];
  filters: AdminListFilters;
  error: string | null;
};

const SECTIONS: Array<ArticleSection | null> = [null, "blog", "news"];

const SORTS: ArticleSort[] = ["new", "views", "likes", "dislikes"];

const SORT_TITLE: Record<ArticleSort, string> = {
  new: "Новые",
  views: "Просмотры",
  likes: "Лайки",
  dislikes: "Дизлайки",
};

const subtitleFor = (list: ArticleAdminList, search: string): string => {
  if (search) return `Найдено: ${list.total}`;
  if (list.total > 0) return `Всего статей: ${list.total}`;

  return "Здесь появятся статьи, когда вы их добавите";
};

const AdminArticles = ({ basePath, list, tags, filters, error }: AdminArticlesProps) => {
  const listPath = `${basePath}/articles`;

  let newHref = `${listPath}/new`;
  if (filters.section) newHref = `${listPath}/new?section=${filters.section}`;

  const sectionTabs = SECTIONS.map((item) => ({
    key: item ?? "all",
    label: item ? SECTION_TITLE[item] : "Все",
    href: buildAdminListHref(listPath, { section: item, sort: filters.sort, search: filters.search }),
  }));

  const sortTabs = SORTS.map((item) => ({
    key: item,
    label: SORT_TITLE[item],
    href: buildAdminListHref(listPath, { section: filters.section, sort: item, search: filters.search }),
  }));

  const listKey = `${filters.section ?? "all"}-${filters.sort}-${filters.search}`;

  return (
    <section className={styles.section}>
      <div className={styles.head}>
        <div className={styles.heading}>
          <h1 className={styles.title}>Статьи</h1>
          <AccentLine width={30} />
          <p className={styles.subtitle}>{subtitleFor(list, filters.search)}</p>
        </div>

        <OutlineButton href={newHref}>Новая статья</OutlineButton>
      </div>

      <TabLinks items={sectionTabs} active={filters.section ?? "all"} label="Раздел" stretch />
      <TabLinks items={sortTabs} active={filters.sort} label="Сортировка" stretch />

      <ArticlesSearch listPath={listPath} filters={filters} />

      {error ? (
        <p className={styles.error}>{error}</p>
      ) : (
        <>
          <TagManager basePath={basePath} initialItems={tags} />
          <ArticlesTable key={listKey} basePath={basePath} initialList={list} filters={filters} />
        </>
      )}
    </section>
  );
};

export default AdminArticles;
