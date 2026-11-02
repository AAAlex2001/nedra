import type {
  EditorAction,
  EditorState,
  ListAction,
  ListState,
  TagsAction,
  TagsState,
} from "./types";

export const editorReducer = (state: EditorState, action: EditorAction): EditorState => {
  switch (action.type) {
    case "field/change":
      return {
        ...state,
        status: "idle",
        fields: { ...state.fields, [action.field]: action.value },
      };

    case "tag/toggle": {
      const has = state.fields.tag_ids.includes(action.id);
      const tag_ids = has
        ? state.fields.tag_ids.filter((id) => id !== action.id)
        : [...state.fields.tag_ids, action.id];

      return { ...state, status: "idle", fields: { ...state.fields, tag_ids } };
    }

    case "document/add":
      return {
        ...state,
        status: "idle",
        fields: { ...state.fields, documents: [...state.fields.documents, action.document] },
      };

    case "document/rename": {
      const documents = state.fields.documents.map((item, index) =>
        index === action.index ? { ...item, title: action.title } : item,
      );

      return { ...state, status: "idle", fields: { ...state.fields, documents } };
    }

    case "document/remove": {
      const documents = state.fields.documents.filter((item, index) => index !== action.index);

      return { ...state, status: "idle", fields: { ...state.fields, documents } };
    }

    case "upload/start":
      return { ...state, uploading: true, error: null };

    case "upload/done":
      return {
        ...state,
        uploading: false,
        fields: { ...state.fields, cover_image: action.url },
      };

    case "upload/error":
      return { ...state, uploading: false, error: action.message };

    case "save/start":
      return { ...state, status: "saving", error: null };

    case "save/done":
      return { ...state, status: "saved" };

    case "save/error":
      return { ...state, status: "error", error: action.message };

    default:
      return state;
  }
};

export const listReducer = (state: ListState, action: ListAction): ListState => {
  switch (action.type) {
    case "delete/start":
      return { ...state, pendingId: action.id, error: null };

    case "delete/done":
      return {
        ...state,
        pendingId: null,
        total: state.total - 1,
        items: state.items.filter((item) => item.id !== action.id),
      };

    case "delete/error":
      return { ...state, pendingId: null, error: action.message };

    case "more/start":
      return { ...state, loadingMore: true, error: null };

    case "more/done":
      return {
        ...state,
        loadingMore: false,
        total: action.total,
        items: [...state.items, ...action.items],
      };

    case "more/error":
      return { ...state, loadingMore: false, error: action.message };

    default:
      return state;
  }
};

export const tagsReducer = (state: TagsState, action: TagsAction): TagsState => {
  switch (action.type) {
    case "draft/change":
      return { ...state, draft: action.value, error: null };

    case "request/start":
      return { ...state, pending: true, error: null };

    case "create/done":
      return {
        ...state,
        pending: false,
        draft: "",
        items: [...state.items, action.tag].sort((a, b) => a.title.localeCompare(b.title, "ru")),
      };

    case "delete/done":
      return {
        ...state,
        pending: false,
        items: state.items.filter((tag) => tag.id !== action.id),
      };

    case "request/error":
      return { ...state, pending: false, error: action.message };

    default:
      return state;
  }
};
