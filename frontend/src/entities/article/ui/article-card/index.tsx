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
  const href = `/blog/${article.slug}`;
  const tag = article.tags[0];

  return (
    <article className={`${styles.card} ${className ?? ""}`}>
      <Link href={href} className={styles.cover} aria-label={article.title}>
        {article.cover_image ? (
          <Image
            src={article.cover_image}
            alt=""
            fill
            unoptimized
            className={styles.image}
          />
        ) : (
          <span className={styles.placeholder} />
        )}
        {tag && <span className={styles.tag}>{tag.title}</span>}
      </Link>

      <div className={styles.body}>
        <h3 className={styles.title}>
          <Link href={href} className={styles.titleLink}>
            {article.title}
          </Link>
        </h3>

        {article.description && (
          <p className={styles.description}>{article.description}</p>
        )}

        <div className={styles.meta}>
          <time className={styles.date} dateTime={article.published_at ?? undefined}>
            {formatDate(article.published_at)}
          </time>
          <Link href={href} className={styles.read}>
            Читать <ArrowRightIcon className={styles.readIcon} />
          </Link>
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
    </article>
  );
};

export default ArticleCard;
