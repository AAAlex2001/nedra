import type { Metadata } from "next";
import type { ArticleAdminCard, TagAdmin } from "@/entities/article";
import { adminBasePath, loadAdmin } from "@/shared/api/server";
import AdminArticles from "@/widgets/admin/articles";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Статьи",
};

export default async function AdminArticlesPage() {
  const [articles, tags] = await Promise.all([
    loadAdmin<ArticleAdminCard[]>("/v1/admin/articles", []),
    loadAdmin<TagAdmin[]>("/v1/admin/tags", []),
  ]);

  return (
    <AdminArticles
      basePath={adminBasePath()}
      articles={articles.data}
      tags={tags.data}
      error={articles.error ?? tags.error}
    />
  );
}
