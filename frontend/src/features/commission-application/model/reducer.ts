import type { ApplicationAction, ApplicationState, AttestationDraft } from "./types";

const EMPTY_DRAFT: AttestationDraft = {
  areaCode: "",
  objectCode: "",
  category: null,
};

export const INITIAL_STATE: ApplicationState = {
  fullName: "",
  draft: EMPTY_DRAFT,
  items: [],
  nextKey: 1,
  status: "idle",
  error: null,
};

export const isDraftComplete = (draft: AttestationDraft): boolean =>
  draft.areaCode !== "" && draft.objectCode !== "" && draft.category !== null;

export const applicationReducer = (
  state: ApplicationState,
  action: ApplicationAction,
): ApplicationState => {
  switch (action.type) {
    case "name/change":
      return { ...state, fullName: action.value };

    case "draft/area":
      return { ...state, draft: { ...state.draft, areaCode: action.code, objectCode: "" } };

    case "draft/object":
      return { ...state, draft: { ...state.draft, objectCode: action.code } };

    case "draft/category":
      return { ...state, draft: { ...state.draft, category: action.category } };

    case "item/add": {
      if (state.draft.category === null || !isDraftComplete(state.draft)) return state;

      const item = {
        key: state.nextKey,
        areaCode: state.draft.areaCode,
        objectCode: state.draft.objectCode,
        category: state.draft.category,
      };

      return {
        ...state,
        items: [...state.items, item],
        nextKey: state.nextKey + 1,
        draft: EMPTY_DRAFT,
      };
    }

    case "item/remove":
      return { ...state, items: state.items.filter((item) => item.key !== action.key) };

    case "submit/start":
      return { ...state, status: "loading", error: null };

    case "submit/success":
      return { ...state, status: "success" };

    case "submit/error":
      return { ...state, status: "error", error: action.message };

    default:
      return state;
  }
};
