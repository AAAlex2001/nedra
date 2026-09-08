import type {
  ArticleAdmin,
  ArticleAdminCard,
  ArticlePayload,
  TagAdmin,
} from "@/entities/article";
import { readErrorMessage } from "@/shared/api";

const requestJson = async <T>(url: string, init?: RequestInit): Promise<T> => {
  const response = await fetch(url, init);

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const data: T = await response.json();

  return data;
};

const requestEmpty = async (url: string, init?: RequestInit): Promise<void> => {
  const response = await fetch(url, init);

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }
};

const jsonBody = (method: string, payload: unknown): RequestInit => ({
  method,
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(payload),
});

export const fetchArticles = (basePath: string) =>
  requestJson<ArticleAdminCard[]>(`${basePath}/api/articles`, { cache: "no-store" });

export const createArticle = (basePath: string, payload: ArticlePayload) =>
  requestJson<ArticleAdmin>(`${basePath}/api/articles`, jsonBody("POST", payload));

export const updateArticle = (basePath: string, id: number, payload: Partial<ArticlePayload>) =>
  requestJson<ArticleAdmin>(`${basePath}/api/articles/${id}`, jsonBody("PATCH", payload));

export const deleteArticle = (basePath: string, id: number) =>
  requestEmpty(`${basePath}/api/articles/${id}`, { method: "DELETE" });

export const uploadImage = (basePath: string, file: File) => {
  const form = new FormData();
  form.append("file", file);

  return requestJson<{ url: string }>(`${basePath}/api/uploads`, {
    method: "POST",
    body: form,
  });
};

export const fetchTags = (basePath: string) =>
  requestJson<TagAdmin[]>(`${basePath}/api/tags`, { cache: "no-store" });

export const createTag = (basePath: string, title: string) =>
  requestJson<TagAdmin>(`${basePath}/api/tags`, jsonBody("POST", { title }));

export const deleteTag = (basePath: string, id: number) =>
  requestEmpty(`${basePath}/api/tags/${id}`, { method: "DELETE" });
