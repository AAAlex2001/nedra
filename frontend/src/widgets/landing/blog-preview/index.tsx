import { ArticleCard, getLatestArticles } from "@/entities/article";
import BlockHeading from "@/shared/ui/block-heading";
import OutlineButton from "@/shared/ui/outline-button";
import { BLOG_PREVIEW_DATA } from "./data";
import styles from "./style.module.scss";

const BlogPreview = async () => {
  const articles = await getLatestArticles(3);

  if (articles.length === 0) return null;

  return (
    <section id="blog" className={styles.section}>
      <BlockHeading title={BLOG_PREVIEW_DATA.title} subtitle={BLOG_PREVIEW_DATA.subtitle} />

      <ul className={styles.grid}>
        {articles.map((article) => (
          <li key={article.slug} className={styles.cell}>
            <ArticleCard article={article} />
          </li>
        ))}
      </ul>

      <OutlineButton href="/blog">{BLOG_PREVIEW_DATA.button}</OutlineButton>
    </section>
  );
};

export default BlogPreview;
