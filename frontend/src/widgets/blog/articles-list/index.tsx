import { ArticleCard, type ArticleList, type Tag } from "@/entities/article";
import { pluralize } from "@/shared/lib/text";
import Button from "@/shared/ui/button";
import TagFilter from "./ui/tag-filter";
import styles from "./style.module.scss";

type ArticlesListProps = {
  basePath: string;
  list: ArticleList;
  tags: Tag[];
  activeTag: string | null;
  page: number;
  emptyText: string;
};

const buildMoreHref = (basePath: string, tag: string | null, page: number) => {
  const params = new URLSearchParams();
  if (tag) params.set("tag", tag);
  params.set("page", String(page));

  return `${basePath}?${params}`;
};

const ArticlesList = ({ basePath, list, tags, activeTag, page, emptyText }: ArticlesListProps) => {
  const hasMore = list.articles.length < list.total;
  const countText = `${list.total} ${pluralize(list.total, ["материал", "материала", "материалов"])}`;

  return (
    <div className={styles.root}>
      {(tags.length > 0 || list.total > 0) && (
        <div className={styles.toolbar}>
          {tags.length > 0 && <TagFilter basePath={basePath} tags={tags} activeTag={activeTag} />}
          {list.total > 0 && <span className={styles.count}>{countText}</span>}
        </div>
      )}

      {list.articles.length === 0 ? (
        <p className={styles.empty}>{emptyText}</p>
      ) : (
        <ul className={styles.grid}>
          {list.articles.map((article) => (
            <li key={article.slug} className={styles.cell}>
              <ArticleCard article={article} />
            </li>
          ))}
        </ul>
      )}

      {hasMore && (
        <div className={styles.more}>
          <Button href={buildMoreHref(basePath, activeTag, page + 1)} scroll={false}>
            Ещё
          </Button>
        </div>
      )}
    </div>
  );
};

export default ArticlesList;
