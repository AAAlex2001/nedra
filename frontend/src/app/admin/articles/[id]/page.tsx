import type { Metadata } from "next";
import { notFound } from "next/navigation";
import type { ArticleAdmin, TagAdmin } from "@/entities/article";
import { adminBasePath, loadAdmin } from "@/shared/api/server";
import ArticleEditor from "@/widgets/admin/article-editor";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Редактирование статьи",
};

type Params = Promise<{ id: string }>;

export default async function EditArticlePage({ params }: { params: Params }) {
  const { id } = await params;
  const articleId = Number(id);

  if (!Number.isInteger(articleId) || articleId <= 0) notFound();

  const [article, tags] = await Promise.all([
    loadAdmin<ArticleAdmin | null>(`/v1/admin/articles/${articleId}`, null),
    loadAdmin<TagAdmin[]>("/v1/admin/tags", []),
  ]);

  if (article.error === "Бэкенд ответил 404") notFound();

  return (
    <ArticleEditor
      basePath={adminBasePath()}
      article={article.data}
      tags={tags.data}
      error={article.error ?? tags.error}
    />
  );
}
