import Image from "next/image";
import Link from "next/link";
import { formatDate } from "@/shared/lib/date";
import {
  ArrowRightIcon,
  EyeIcon,
  ThumbDownIcon,
  ThumbUpIcon,
} from "@/shared/ui/icons";
import type { ArticleCard as ArticleCardType } from "../../model/types";
import styles from "./style.module.scss";

type ArticleCardProps = {
  article: ArticleCardType;
  className?: string;
};

const ArticleCard = ({ article, className }: ArticleCardProps) => {
  const tag = article.tags[0];

  return (
    <Link href={`/blog/${article.slug}`} className={`${styles.card} ${className ?? ""}`}>
      <div className={styles.cover}>
        {article.cover_image ? (
          <Image
            src={article.cover_image}
            alt=""
            fill
            unoptimized
            className={styles.image}
          />
        ) : (
          <div className={styles.placeholder} />
        )}
        {tag && <span className={styles.tag}>{tag.title}</span>}
      </div>

      <div className={styles.body}>
        <h3 className={styles.title}>{article.title}</h3>

        {article.description && (
          <p className={styles.description}>{article.description}</p>
        )}

        <div className={styles.meta}>
          <time className={styles.date} dateTime={article.published_at ?? undefined}>
            {formatDate(article.published_at)}
          </time>
          <span className={styles.read}>
            Читать <ArrowRightIcon className={styles.readIcon} />
          </span>
        </div>

        <div className={styles.stats}>
          <span className={styles.stat}>
            <ThumbUpIcon className={styles.statIcon} />
            {article.likes_count}
          </span>
          <span className={styles.stat}>
            <ThumbDownIcon className={styles.statIcon} />
            {article.dislikes_count}
          </span>
          <span className={`${styles.stat} ${styles.views}`}>
            <EyeIcon className={styles.statIcon} />
            {article.views_count}
          </span>
        </div>
      </div>
    </Link>
  );
};

export default ArticleCard;
