"use client";

import Image from "next/image";
import Link from "next/link";
import { SECTION_TITLE, type ArticleAdminCard } from "@/entities/article";
import { formatDate, isFutureDate } from "@/shared/lib/date";
import { EyeIcon, ThumbDownIcon, ThumbUpIcon } from "@/shared/ui/icons";
import { useArticlesList } from "../../model/use-articles-list";
import styles from "./style.module.scss";

type ArticlesTableProps = {
  basePath: string;
  initialItems: ArticleAdminCard[];
};

const ArticlesTable = ({ basePath, initialItems }: ArticlesTableProps) => {
  const { state, remove } = useArticlesList(basePath, initialItems);

  if (state.items.length === 0) {
    return <p className={styles.empty}>Статей пока нет — создайте первую.</p>;
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
          if (isFutureDate(article.published_at)) {
            statusClass = styles.statusScheduled;
            statusText = "Запланирована";
          } else if (article.published_at) {
            statusClass = styles.statusPublished;
            statusText = "Опубликована";
          }

          return (
            <li
              key={article.id}
              className={`${styles.row} ${pending ? styles.rowPending : ""}`}
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
                  <span className={`${styles.status} ${statusClass}`}>{statusText}</span>
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
                <button
                  type="button"
                  className={styles.delete}
                  disabled={pending}
                  onClick={() => {
                    if (window.confirm(`Удалить статью «${article.title}»?`)) {
                      void remove(article.id);
                    }
                  }}
                >
                  {pending ? "Удаляем…" : "Удалить"}
                </button>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
};

export default ArticlesTable;
