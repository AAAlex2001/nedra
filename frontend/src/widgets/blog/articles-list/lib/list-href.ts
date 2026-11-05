import type { PublishedArticleSort } from "@/entities/article/lib/sorting";

type ListQuery = {
  tag: string | null;
  search: string;
  page?: number;
  sort: PublishedArticleSort;
};

export const buildListHref = (basePath: string, { tag, search, page, sort }: ListQuery): string => {
  const params = new URLSearchParams();

  if (sort !== "newest") params.set("sort", sort);
  if (tag) params.set("tag", tag);
  if (search) params.set("q", search);
  if (page && page > 1) params.set("page", String(page));

  const query = params.toString();

  return query ? `${basePath}?${query}` : basePath;
};
