import type { Metadata } from "next";
import type { TagAdmin } from "@/entities/article";
import { adminBasePath, loadAdmin } from "@/shared/api/server";
import ArticleEditor from "@/widgets/admin/article-editor";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Новая статья",
};

export default async function NewArticlePage() {
  const tags = await loadAdmin<TagAdmin[]>("/v1/admin/tags", []);

  return (
    <ArticleEditor
      basePath={adminBasePath()}
      article={null}
      tags={tags.data}
      error={tags.error}
    />
  );
}
