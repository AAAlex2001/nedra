import { ArticlesSlider, getLatestArticles, type ArticleCardData } from "@/entities/article";
import BlockHeading from "@/shared/ui/block-heading";
import OutlineButton from "@/shared/ui/outline-button";
import { BLOG_PREVIEW_DATA } from "./data";
import styles from "./style.module.scss";

const loadPreview = async (): Promise<ArticleCardData[]> => {
  const blog = await getLatestArticles("blog", BLOG_PREVIEW_DATA.limit);

  const remaining = BLOG_PREVIEW_DATA.limit - blog.length;
  if (remaining <= 0) return blog;

  const news = await getLatestArticles("news", remaining);

  return [...blog, ...news];
};

const BlogPreview = async () => {
  const articles = await loadPreview();

  if (articles.length === 0) return null;

  return (
    <section id="blog" className={styles.section}>
      <BlockHeading title={BLOG_PREVIEW_DATA.title} subtitle={BLOG_PREVIEW_DATA.subtitle} />

      <ArticlesSlider articles={articles} ariaLabel={BLOG_PREVIEW_DATA.title} />

      <div className={styles.actions}>
        <OutlineButton href="/blog">{BLOG_PREVIEW_DATA.blogButton}</OutlineButton>
        <OutlineButton href="/novosti">{BLOG_PREVIEW_DATA.newsButton}</OutlineButton>
      </div>
    </section>
  );
};

export default BlogPreview;
