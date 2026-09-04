import type { RequestFormAction, RequestFormState } from "./types";

export const INITIAL_STATE: RequestFormState = {
  directionId: "",
  serviceId: "",
  fields: {
    name: "",
    telephone: "",
    email: "",
    companyName: "",
    inn: "",
    comment: "",
  },
  status: "idle",
  error: null,
};

export const requestFormReducer = (
  state: RequestFormState,
  action: RequestFormAction,
): RequestFormState => {
  switch (action.type) {
    case "direction/select":
      return { ...state, directionId: action.id, serviceId: "", error: null };

    case "service/select":
      return { ...state, serviceId: action.id, error: null };

    case "field/change":
      return {
        ...state,
        fields: { ...state.fields, [action.field]: action.value },
      };

    case "submit/start":
      return { ...state, status: "loading", error: null };

    case "submit/success":
      return { ...INITIAL_STATE, status: "success" };

    case "submit/error":
      return { ...state, status: "error", error: action.message };

    case "form/reset":
      return INITIAL_STATE;

    default:
      return state;
  }
};
