export const ARTICLE_SORT_OPTIONS = [
  { value: "newest", label: "Сначала новые" },
  { value: "oldest", label: "Сначала старые" },
  { value: "views_desc", label: "Просмотры: больше сначала" },
  { value: "views_asc", label: "Просмотры: меньше сначала" },
  { value: "likes_desc", label: "Лайки: больше сначала" },
  { value: "likes_asc", label: "Лайки: меньше сначала" },
  { value: "dislikes_desc", label: "Дизлайки: больше сначала" },
  { value: "dislikes_asc", label: "Дизлайки: меньше сначала" },
] as const;

export type PublishedArticleSort = (typeof ARTICLE_SORT_OPTIONS)[number]["value"];

export const parseArticleSort = (value?: string): PublishedArticleSort =>
  ARTICLE_SORT_OPTIONS.find((option) => option.value === value)?.value ?? "newest";
