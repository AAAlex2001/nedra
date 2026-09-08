import type { Metadata } from "next";
import type { ArticleAdminCard, ArticleSection, TagAdmin } from "@/entities/article";
import { adminBasePath, loadAdmin } from "@/shared/api/server";
import AdminArticles from "@/widgets/admin/articles";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Статьи",
};

type SearchParams = Promise<{ section?: string }>;

export default async function AdminArticlesPage({
  searchParams,
}: {
  searchParams: SearchParams;
}) {
  const { section } = await searchParams;

  let activeSection: ArticleSection | null = null;
  if (section === "blog" || section === "news") activeSection = section;

  let listPath = "/v1/admin/articles";
  if (activeSection) listPath = `${listPath}?section=${activeSection}`;

  const [articles, tags] = await Promise.all([
    loadAdmin<ArticleAdminCard[]>(listPath, []),
    loadAdmin<TagAdmin[]>("/v1/admin/tags", []),
  ]);

  return (
    <AdminArticles
      basePath={adminBasePath()}
      articles={articles.data}
      tags={tags.data}
      section={activeSection}
      error={articles.error ?? tags.error}
    />
  );
}
