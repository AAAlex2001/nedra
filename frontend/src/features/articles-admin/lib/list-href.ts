import type { ArticleSection, ArticleSort } from "@/entities/article";

export type AdminListFilters = {
  section: ArticleSection | null;
  sort: ArticleSort;
  search: string;
};

export const ADMIN_PAGE_SIZE = 20;

export const buildAdminListHref = (listPath: string, filters: AdminListFilters): string => {
  const params = new URLSearchParams();

  if (filters.section) params.set("section", filters.section);
  if (filters.sort !== "new") params.set("sort", filters.sort);
  if (filters.search) params.set("q", filters.search);

  const query = params.toString();

  return query ? `${listPath}?${query}` : listPath;
};
