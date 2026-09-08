import type { Metadata } from "next";
import type { ArticleSection, TagAdmin } from "@/entities/article";
import { adminBasePath, loadAdmin } from "@/shared/api/server";
import ArticleEditor from "@/widgets/admin/article-editor";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Новая статья",
};

type SearchParams = Promise<{ section?: string }>;

export default async function NewArticlePage({
  searchParams,
}: {
  searchParams: SearchParams;
}) {
  const { section } = await searchParams;
  const tags = await loadAdmin<TagAdmin[]>("/v1/admin/tags", []);

  let initialSection: ArticleSection = "blog";
  if (section === "news") initialSection = "news";

  return (
    <ArticleEditor
      basePath={adminBasePath()}
      article={null}
      tags={tags.data}
      section={initialSection}
      error={tags.error}
    />
  );
}
