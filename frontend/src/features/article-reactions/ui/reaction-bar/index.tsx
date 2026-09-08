"use client";

import type { ArticleStats } from "@/entities/article";
import { EyeIcon, ThumbDownIcon, ThumbUpIcon } from "@/shared/ui/icons";
import { useArticleStats } from "../../model/use-article-stats";
import styles from "./style.module.scss";

type ReactionBarProps = {
  slug: string;
  initial: ArticleStats;
};

const ReactionBar = ({ slug, initial }: ReactionBarProps) => {
  const { stats, pending, error, react } = useArticleStats(slug, initial);

  return (
    <div className={styles.wrap}>
      <div className={styles.bar}>
        <span className={styles.label}>Была полезна статья?</span>

        <button
          type="button"
          className={`${styles.button} ${stats.my_reaction === 1 ? styles.active : ""}`}
          aria-pressed={stats.my_reaction === 1}
          aria-label="Полезно"
          disabled={pending}
          onClick={() => void react(1)}
        >
          <ThumbUpIcon className={styles.icon} />
          {stats.likes_count}
        </button>

        <button
          type="button"
          className={`${styles.button} ${stats.my_reaction === -1 ? styles.active : ""}`}
          aria-pressed={stats.my_reaction === -1}
          aria-label="Не полезно"
          disabled={pending}
          onClick={() => void react(-1)}
        >
          <ThumbDownIcon className={styles.icon} />
          {stats.dislikes_count}
        </button>

        <span className={styles.views}>
          <EyeIcon className={styles.icon} />
          {stats.views_count}
        </span>
      </div>

      {error && <p className={styles.error}>{error}</p>}
    </div>
  );
};

export default ReactionBar;
