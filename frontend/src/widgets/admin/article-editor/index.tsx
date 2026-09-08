import type { ArticleAdmin, ArticleSection, TagAdmin } from "@/entities/article";
import { ArticleForm } from "@/features/articles-admin";
import AccentLine from "@/shared/ui/accent-line";
import styles from "./style.module.scss";

type ArticleEditorProps = {
  basePath: string;
  article: ArticleAdmin | null;
  tags: TagAdmin[];
  section: ArticleSection;
  error: string | null;
};

const ArticleEditor = ({ basePath, article, tags, section, error }: ArticleEditorProps) => {
  return (
    <section className={styles.section}>
      <div className={styles.heading}>
        <h1 className={styles.title}>{article ? "Редактирование статьи" : "Новая статья"}</h1>
        <AccentLine width={30} />
      </div>

      {error ? (
        <p className={styles.error}>{error}</p>
      ) : (
        <ArticleForm basePath={basePath} article={article} tags={tags} section={section} />
      )}
    </section>
  );
};

export default ArticleEditor;
