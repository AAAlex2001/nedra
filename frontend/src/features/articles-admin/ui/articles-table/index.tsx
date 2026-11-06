"use client";

import classNames from "classnames";
import Image from "next/image";
import Link from "next/link";
import { SECTION_TITLE, articlePath, type ArticleAdminList } from "@/entities/article";
import { formatDate, isFutureDate } from "@/shared/lib/date";
import Button from "@/shared/ui/button";
import DeleteButton from "@/shared/ui/delete-button";
import { EyeIcon, ThumbDownIcon, ThumbUpIcon } from "@/shared/ui/icons";
import Spinner from "@/shared/ui/spinner";
import type { AdminListFilters } from "../../lib/list-href";
import { useArticlesList } from "../../model/use-articles-list";
import styles from "./style.module.scss";

type ArticlesTableProps = {
  basePath: string;
  initialList: ArticleAdminList;
  filters: AdminListFilters;
};

const ArticlesTable = ({ basePath, initialList, filters }: ArticlesTableProps) => {
  const { state, hasMore, remove, loadMore } = useArticlesList(basePath, initialList, filters);

  if (state.items.length === 0) {
    const emptyText = filters.search
      ? `По запросу «${filters.search}» ничего не найдено.`
      : "Статей пока нет — создайте первую.";

    return <p className={styles.empty}>{emptyText}</p>;
  }

  return (
    <div className={styles.root}>
      {state.error && <p className={styles.error}>{state.error}</p>}

      <ul className={styles.list}>
        {state.items.map((article) => {
          const pending = state.pendingId === article.id;
          const editHref = `${basePath}/articles/${article.id}`;

          let statusClass = styles.statusDraft;
          let statusText = "Черновик";
          let published = false;
          if (isFutureDate(article.published_at)) {
            statusClass = styles.statusScheduled;
            statusText = "Запланирована";
          } else if (article.published_at) {
            statusClass = styles.statusPublished;
            statusText = "Опубликована";
            published = true;
          }

          return (
            <li
              key={article.id}
              className={classNames(styles.row, pending && styles.rowPending)}
            >
              <Link href={editHref} className={styles.thumb}>
                {article.cover_image && (
                  <Image src={article.cover_image} alt="" fill unoptimized className={styles.thumbImage} />
                )}
              </Link>

              <div className={styles.info}>
                <Link href={editHref} className={styles.title}>
                  {article.title}
                </Link>

                <div className={styles.meta}>
                  <span className={classNames(styles.status, statusClass)}>{statusText}</span>
                  <span className={styles.section}>{SECTION_TITLE[article.section]}</span>
                  <span className={styles.date}>
                    {formatDate(article.published_at ?? article.created_at)}
                  </span>
                  {article.tags.map((tag) => (
                    <span key={tag.id} className={styles.tag}>
                      {tag.title}
                    </span>
                  ))}
                </div>
              </div>

              <div className={styles.stats}>
                <span className={styles.stat}>
                  <EyeIcon className={styles.statIcon} />
                  {article.views_count}
                </span>
                <span className={styles.stat}>
                  <ThumbUpIcon className={styles.statIcon} />
                  {article.likes_count}
                </span>
                <span className={styles.stat}>
                  <ThumbDownIcon className={styles.statIcon} />
                  {article.dislikes_count}
                </span>
              </div>

              <div className={styles.actions}>
                <Link href={editHref} className={styles.edit}>
                  Редактировать
                </Link>
                {published && (
                  <Link
                    href={articlePath(article)}
                    className={styles.view}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Перейти
                  </Link>
                )}
                <DeleteButton
                  className={styles.delete}
                  disabled={pending}
                  title="Удалить публикацию?"
                  description={`Публикация «${article.title}» будет удалена без возможности восстановления.`}
                  onConfirm={() => remove(article.id)}
                >
                  {pending ? <Spinner size={14} /> : "Удалить"}
                </DeleteButton>
              </div>
            </li>
          );
        })}
      </ul>

      {hasMore && (
        <Button className={styles.more} loading={state.loadingMore} onClick={() => void loadMore()}>
          Загрузить ещё
        </Button>
      )}
    </div>
  );
};

export default ArticlesTable;
