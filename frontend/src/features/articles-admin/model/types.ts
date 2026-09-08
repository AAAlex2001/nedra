import type { ArticleAdminCard, TagAdmin } from "@/entities/article";

export type EditorFields = {
  title: string;
  slug: string;
  description: string;
  cover_image: string;
  content: string;
  tag_ids: number[];
  published: boolean;
  seo_title: string;
  seo_description: string;
  seo_keywords: string;
};

export type EditorStatus = "idle" | "saving" | "saved" | "error";

export type EditorState = {
  fields: EditorFields;
  status: EditorStatus;
  uploading: boolean;
  error: string | null;
};

export type EditorAction =
  | { type: "field/change"; field: keyof EditorFields; value: string | boolean }
  | { type: "tag/toggle"; id: number }
  | { type: "upload/start" }
  | { type: "upload/done"; url: string }
  | { type: "upload/error"; message: string }
  | { type: "save/start" }
  | { type: "save/done" }
  | { type: "save/error"; message: string };

export type ListState = {
  items: ArticleAdminCard[];
  pendingId: number | null;
  error: string | null;
};

export type ListAction =
  | { type: "delete/start"; id: number }
  | { type: "delete/done"; id: number }
  | { type: "delete/error"; message: string };

export type TagsState = {
  items: TagAdmin[];
  draft: string;
  pending: boolean;
  error: string | null;
};

export type TagsAction =
  | { type: "draft/change"; value: string }
  | { type: "request/start" }
  | { type: "create/done"; tag: TagAdmin }
  | { type: "delete/done"; id: number }
  | { type: "request/error"; message: string };
