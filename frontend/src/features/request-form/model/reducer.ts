import type {
  RequestFields,
  RequestFormAction,
  RequestFormState,
} from "./types";

const EMPTY_FIELDS: RequestFields = {
  name: "",
  telephone: "",
  email: "",
  companyName: "",
  inn: "",
  comment: "",
};

export const INITIAL_STATE: RequestFormState = {
  directionId: null,
  serviceId: null,
  fields: EMPTY_FIELDS,
  status: "idle",
  error: null,
  submitted: false,
};

export const requestFormReducer = (
  state: RequestFormState,
  action: RequestFormAction,
): RequestFormState => {
  switch (action.type) {
    case "direction/select":
      // Смена направления сбрасывает услугу: старая к новому не относится.
      return {
        ...state,
        directionId: action.id,
        serviceId: null,
        error: null,
      };

    case "service/select":
      return { ...state, serviceId: action.id, error: null };

    case "field/change":
      return {
        ...state,
        fields: { ...state.fields, [action.field]: action.value },
      };

    case "submit/start":
      return { ...state, status: "loading", error: null, submitted: true };

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
