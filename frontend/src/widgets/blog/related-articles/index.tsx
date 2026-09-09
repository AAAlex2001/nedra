import { ArticlesSlider, type ArticleCardData } from "@/entities/article";

type RelatedArticlesProps = {
  articles: ArticleCardData[];
};

const RelatedArticles = ({ articles }: RelatedArticlesProps) => (
  <ArticlesSlider articles={articles} title="Смотрите также" ariaLabel="Смотрите также" />
);

export default RelatedArticles;
