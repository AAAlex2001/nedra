import type { Metadata } from "next";
import type { ArticleAdminList, ArticleSection, ArticleSort, TagAdmin } from "@/entities/article";
import { buildAdminListHref, type AdminListFilters } from "@/features/articles-admin";
import { adminBasePath, loadAdmin } from "@/shared/api/server";
import AdminArticles from "@/widgets/admin/articles";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Статьи",
};

type SearchParams = Promise<{ section?: string; sort?: string; q?: string }>;

const EMPTY_LIST: ArticleAdminList = { articles: [], total: 0 };

export default async function AdminArticlesPage({
  searchParams,
}: {
  searchParams: SearchParams;
}) {
  const { section, sort, q } = await searchParams;

  let activeSection: ArticleSection | null = null;
  if (section === "blog" || section === "news") activeSection = section;

  let activeSort: ArticleSort = "new";
  if (sort === "views" || sort === "likes" || sort === "dislikes") activeSort = sort;

  const filters: AdminListFilters = {
    section: activeSection,
    sort: activeSort,
    search: q?.trim() ?? "",
  };

  const listPath = buildAdminListHref("/v1/admin/articles", filters);

  const [list, tags] = await Promise.all([
    loadAdmin<ArticleAdminList>(listPath, EMPTY_LIST),
    loadAdmin<TagAdmin[]>("/v1/admin/tags", []),
  ]);

  return (
    <AdminArticles
      basePath={adminBasePath()}
      list={list.data}
      tags={tags.data}
      filters={filters}
      error={list.error ?? tags.error}
    />
  );
}
