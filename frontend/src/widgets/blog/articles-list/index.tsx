"use client";

import { useRouter } from "next/navigation";
import { useTransition } from "react";
import {
  ArticleCard,
  SECTION_PATH,
  type ArticleList,
  type ArticleSection,
  type Tag,
} from "@/entities/article";
import Button from "@/shared/ui/button";
import Spinner from "@/shared/ui/spinner";
import { buildListHref } from "./lib/list-href";
import SearchForm from "./ui/search-form";
import TagFilter from "./ui/tag-filter";
import styles from "./style.module.scss";

type ArticlesListProps = {
  section: ArticleSection;
  list: ArticleList;
  tags: Tag[];
  activeTag: string | null;
  search: string;
  page: number;
  emptyText: string;
};

const ArticlesList = ({
  section,
  list,
  tags,
  activeTag,
  search,
  page,
  emptyText,
}: ArticlesListProps) => {
  const router = useRouter();
  const [pending, startTransition] = useTransition();

  const basePath = SECTION_PATH[section];
  const hasMore = list.articles.length < list.total;
  const emptyMessage = search ? `По запросу «${search}» ничего не найдено.` : emptyText;
  const moreHref = buildListHref(basePath, { tag: activeTag, search, page: page + 1 });

  const runSearch = (value: string) => {
    const href = buildListHref(basePath, { tag: activeTag, search: value });

    startTransition(() => router.push(href, { scroll: false }));
  };

  return (
    <div className={styles.root}>
      <div className={styles.toolbar}>
        {tags.length > 0 && (
          <TagFilter basePath={basePath} tags={tags} activeTag={activeTag} search={search} />
        )}
        <SearchForm
          key={search}
          section={section}
          initialValue={search}
          pending={pending}
          onSearch={runSearch}
        />
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
