import type { ApplicationFormAction, ApplicationFormState, CertificateDraft } from "./types";

export const EMPTY_DRAFT: CertificateDraft = {
  areaCode: "",
  objectCode: "",
  category: null,
  validUntil: "",
  number: "",
};

export const INITIAL_STATE: ApplicationFormState = {
  fields: { fullName: "", email: "", phone: "", password: "" },
  directions: [],
  draft: EMPTY_DRAFT,
  certificates: [],
  nextKey: 1,
  status: "idle",
  error: null,
};

export const isDraftComplete = (draft: CertificateDraft): boolean =>
  draft.areaCode !== "" &&
  draft.objectCode !== "" &&
  draft.category !== null &&
  draft.validUntil !== "" &&
  draft.number.trim() !== "";

export const applicationFormReducer = (
  state: ApplicationFormState,
  action: ApplicationFormAction,
): ApplicationFormState => {
  switch (action.type) {
    case "field/change":
      return {
        ...state,
        fields: { ...state.fields, [action.field]: action.value },
        error: null,
      };

    case "direction/toggle": {
      const selected = state.directions.includes(action.code);
      const directions = selected
        ? state.directions.filter((code) => code !== action.code)
        : [...state.directions, action.code];

      return { ...state, directions, error: null };
    }

    case "draft/area":
      return { ...state, draft: { ...state.draft, areaCode: action.code, objectCode: "" } };

    case "draft/object":
      return { ...state, draft: { ...state.draft, objectCode: action.code } };

    case "draft/category":
      return { ...state, draft: { ...state.draft, category: action.category } };

    case "draft/date":
      return { ...state, draft: { ...state.draft, validUntil: action.value } };

    case "draft/number":
      return { ...state, draft: { ...state.draft, number: action.value } };

    case "certificate/add": {
      if (!isDraftComplete(state.draft)) return state;

      const item = { ...state.draft, key: state.nextKey };

      return {
        ...state,
        certificates: [...state.certificates, item],
        draft: EMPTY_DRAFT,
        nextKey: state.nextKey + 1,
        error: null,
      };
    }

    case "certificate/remove":
      return {
        ...state,
        certificates: state.certificates.filter((item) => item.key !== action.key),
      };

    case "submit/start":
      return { ...state, status: "loading", error: null };

    case "submit/success":
      return { ...INITIAL_STATE, status: "success" };

    case "submit/error":
      return { ...state, status: "error", error: action.message };

    case "success/close":
      return { ...state, status: "idle" };

    default:
      return state;
  }
};
