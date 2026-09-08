export type ArticleSection = "blog" | "news";

export type Tag = {
  slug: string;
  title: string;
};

export type TagAdmin = Tag & {
  id: number;
};

export type TocItem = {
  id: string;
  title: string;
};

export type ArticleCard = {
  slug: string;
  section: ArticleSection;
  title: string;
  description: string | null;
  cover_image: string | null;
  published_at: string | null;
  views_count: number;
  likes_count: number;
  dislikes_count: number;
  tags: Tag[];
};

export type ArticleSeo = {
  seo_title: string | null;
  seo_description: string | null;
  seo_keywords: string | null;
};

export type Article = ArticleCard &
  ArticleSeo & {
    content: string;
    toc: TocItem[];
  };

export type ArticleList = {
  articles: ArticleCard[];
  total: number;
};

export type ArticleStats = {
  views_count: number;
  likes_count: number;
  dislikes_count: number;
  my_reaction: 1 | -1 | null;
};

export type ArticleAdminCard = Omit<ArticleCard, "tags"> & {
  id: number;
  created_at: string;
  updated_at: string;
  tags: TagAdmin[];
};

export type ArticleAdmin = ArticleAdminCard &
  ArticleSeo & {
    content: string;
    toc: TocItem[];
  };

export type ArticlePayload = ArticleSeo & {
  title: string;
  slug: string | null;
  section: ArticleSection;
  description: string | null;
  cover_image: string | null;
  content: string;
  tag_ids: number[];
  published: boolean;
  published_at: string | null;
};
