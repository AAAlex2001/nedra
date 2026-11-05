"use client";

import classNames from "classnames";
import { useRouter } from "next/navigation";
import { useTransition } from "react";
import {
  ArticleCard,
  ARTICLE_SORT_OPTIONS,
  SECTION_PATH,
  type ArticleList,
  type ArticleSection,
  type PublishedArticleSort,
  type Tag,
} from "@/entities/article";
import Button from "@/shared/ui/button";
import SearchForm from "@/shared/ui/search-form";
import Spinner from "@/shared/ui/spinner";
import { buildListHref } from "./lib/list-href";
import ListFilter from "./ui/list-filter";
import TagFilter from "./ui/tag-filter";
import styles from "./style.module.scss";

type ArticlesListProps = {
  section: ArticleSection;
  list: ArticleList;
  tags: Tag[];
  activeTag: string | null;
  search: string;
  page: number;
  sort: PublishedArticleSort;
  emptyText: string;
};

const ArticlesList = ({
  section,
  list,
  tags,
  activeTag,
  search,
  page,
  sort,
  emptyText,
}: ArticlesListProps) => {
  const router = useRouter();
  const [pending, startTransition] = useTransition();

  const basePath = SECTION_PATH[section];
  const hasMore = list.articles.length < list.total;
  const emptyMessage = search ? `По запросу «${search}» ничего не найдено.` : emptyText;
  const moreHref = buildListHref(basePath, { tag: activeTag, search, sort, page: page + 1 });

  const runSearch = (value: string) => {
    const href = buildListHref(basePath, { tag: activeTag, search: value, sort });

    startTransition(() => router.replace(href, { scroll: false }));
  };

  return (
    <div className={styles.root}>
      <div className={classNames(styles.toolbar, tags.length === 0 && styles.toolbarWithoutTags)}>
        {tags.length > 0 && (
          <TagFilter
            basePath={basePath}
            tags={tags}
            activeTag={activeTag}
            search={search}
            sort={sort}
          />
        )}
        <ListFilter
          label="Сортировка"
          value={sort}
          highlighted={sort !== "newest"}
          options={ARTICLE_SORT_OPTIONS.map((option) => ({
            ...option,
            href: buildListHref(basePath, { tag: activeTag, search, sort: option.value }),
          }))}
        />
        <div className={styles.search}>
          <SearchForm initialValue={search} pending={pending} onSearch={runSearch} />
        </div>
      </div>

      <div className={styles.results} aria-busy={pending}>
        {list.articles.length === 0 ? (
          <p className={styles.empty}>{emptyMessage}</p>
        ) : (
          <ul className={styles.grid}>
            {list.articles.map((article) => (
              <li key={article.slug} className={styles.cell}>
                <ArticleCard article={article} compact />
              </li>
            ))}
          </ul>
        )}

        {pending && (
          <div className={styles.overlay}>
            <Spinner size={36} />
          </div>
        )}
      </div>

      {hasMore && (
        <div className={styles.more}>
          <Button href={moreHref} scroll={false}>
            Ещё
          </Button>
        </div>
      )}
    </div>
  );
};

export default ArticlesList;
