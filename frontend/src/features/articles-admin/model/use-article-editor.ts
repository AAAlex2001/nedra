"use client";

import { useReducer } from "react";
import type { ArticleAdmin, ArticlePayload } from "@/entities/article";
import { createArticle, updateArticle, uploadImage } from "../api/admin-articles";
import { editorReducer } from "./reducers";
import type { EditorFields } from "./types";

const toFields = (article: ArticleAdmin | null): EditorFields => ({
  title: article?.title ?? "",
  slug: article?.slug ?? "",
  description: article?.description ?? "",
  cover_image: article?.cover_image ?? "",
  content: article?.content ?? "",
  tag_ids: article?.tags.map((tag) => tag.id) ?? [],
  published: Boolean(article?.published_at),
});

const toPayload = (fields: EditorFields): ArticlePayload => ({
  title: fields.title.trim(),
  slug: fields.slug.trim() || null,
  description: fields.description.trim() || null,
  cover_image: fields.cover_image.trim() || null,
  content: fields.content,
  tag_ids: fields.tag_ids,
  published: fields.published,
});

const errorText = (error: unknown, fallback: string) =>
  error instanceof Error ? error.message : fallback;

export const useArticleEditor = (basePath: string, article: ArticleAdmin | null) => {
  const [state, dispatch] = useReducer(editorReducer, {
    fields: toFields(article),
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
      const saved = article
        ? await updateArticle(basePath, article.id, payload)
        : await createArticle(basePath, payload);

      dispatch({ type: "save/done" });
      return saved;
    } catch (error) {
      dispatch({ type: "save/error", message: errorText(error, "Не удалось сохранить статью") });
      return null;
    }
  };

  return { state, changeField, toggleTag, uploadCover, save };
};
