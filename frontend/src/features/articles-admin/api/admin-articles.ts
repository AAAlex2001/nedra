import type {
  ArticleAdmin,
  ArticleAdminCard,
  ArticlePayload,
  TagAdmin,
} from "@/entities/article";
import { readErrorMessage } from "@/shared/api";

const json = async <T>(response: Response): Promise<T> => {
  if (!response.ok) throw new Error(await readErrorMessage(response));

  return (await response.json()) as T;
};

const ensureOk = async (response: Response): Promise<void> => {
  if (!response.ok) throw new Error(await readErrorMessage(response));
};

export const fetchArticles = (basePath: string) =>
  fetch(`${basePath}/api/articles`, { cache: "no-store" }).then(json<ArticleAdminCard[]>);

export const createArticle = (basePath: string, payload: ArticlePayload) =>
  fetch(`${basePath}/api/articles`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  }).then(json<ArticleAdmin>);

export const updateArticle = (basePath: string, id: number, payload: Partial<ArticlePayload>) =>
  fetch(`${basePath}/api/articles/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  }).then(json<ArticleAdmin>);

export const deleteArticle = (basePath: string, id: number) =>
  fetch(`${basePath}/api/articles/${id}`, { method: "DELETE" }).then(ensureOk);

export const uploadImage = (basePath: string, file: File) => {
  const form = new FormData();
  form.append("file", file);

  return fetch(`${basePath}/api/uploads`, { method: "POST", body: form }).then(
    json<{ url: string }>,
  );
};

export const fetchTags = (basePath: string) =>
  fetch(`${basePath}/api/tags`, { cache: "no-store" }).then(json<TagAdmin[]>);

export const createTag = (basePath: string, title: string) =>
  fetch(`${basePath}/api/tags`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  }).then(json<TagAdmin>);

export const deleteTag = (basePath: string, id: number) =>
  fetch(`${basePath}/api/tags/${id}`, { method: "DELETE" }).then(ensureOk);
