"use client";

import { useReducer } from "react";
import type { ArticleAdmin, ArticlePayload, ArticleSection } from "@/entities/article";
import { toDateTimeInput } from "@/shared/lib/date";
import { createArticle, updateArticle, uploadImage } from "../api/admin-articles";
import { editorReducer } from "./reducers";
import type { EditorFields } from "./types";

const toFields = (article: ArticleAdmin | null, section: ArticleSection): EditorFields => ({
  title: article?.title ?? "",
  slug: article?.slug ?? "",
  section: article?.section ?? section,
  description: article?.description ?? "",
  cover_image: article?.cover_image ?? "",
  content: article?.content ?? "",
  tag_ids: article?.tags.map((tag) => tag.id) ?? [],
  published: Boolean(article?.published_at),
  published_at: toDateTimeInput(article?.published_at),
  seo_title: article?.seo_title ?? "",
  seo_description: article?.seo_description ?? "",
  seo_keywords: article?.seo_keywords ?? "",
});

const toPayload = (fields: EditorFields): ArticlePayload => {
  let publishedAt: string | null = null;
  if (fields.published_at) {
    publishedAt = new Date(fields.published_at).toISOString();
  }

  return {
    title: fields.title.trim(),
    slug: fields.slug.trim() || null,
    section: fields.section,
    description: fields.description.trim() || null,
    cover_image: fields.cover_image.trim() || null,
    content: fields.content,
    tag_ids: fields.tag_ids,
    published: fields.published,
    published_at: publishedAt,
    seo_title: fields.seo_title.trim() || null,
    seo_description: fields.seo_description.trim() || null,
    seo_keywords: fields.seo_keywords.trim() || null,
  };
};

const errorText = (error: unknown, fallback: string) =>
  error instanceof Error ? error.message : fallback;

export const useArticleEditor = (
  basePath: string,
  article: ArticleAdmin | null,
  section: ArticleSection,
) => {
  const [state, dispatch] = useReducer(editorReducer, {
    fields: toFields(article, section),
    status: "idle",
    uploading: false,
    error: null,
  });

  const changeField = (field: keyof EditorFields, value: string | boolean) =>
    dispatch({ type: "field/change", field, value });

  const toggleTag = (id: number) => dispatch({ type: "tag/toggle", id });

  const uploadCover = async (file: File) => {
    dispatch({ type: "upload/start" });

    try {
      const { url } = await uploadImage(basePath, file);
      dispatch({ type: "upload/done", url });
    } catch (error) {
      dispatch({ type: "upload/error", message: errorText(error, "Не удалось загрузить файл") });
    }
  };

  const save = async (): Promise<ArticleAdmin | null> => {
    dispatch({ type: "save/start" });

    try {
      const payload = toPayload(state.fields);

      let saved: ArticleAdmin;
      if (article) {
        saved = await updateArticle(basePath, article.id, payload);
      } else {
        saved = await createArticle(basePath, payload);
      }

      dispatch({ type: "save/done" });
      return saved;
    } catch (error) {
      dispatch({ type: "save/error", message: errorText(error, "Не удалось сохранить статью") });
      return null;
    }
  };

  return { state, changeField, toggleTag, uploadCover, save };
};
