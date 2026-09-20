import type { RegisterFormAction, RegisterFormState } from "./types";

export const INITIAL_REGISTER: RegisterFormState = {
  fields: { fullName: "", email: "", phone: "", password: "" },
  status: "idle",
  error: null,
};

export const registerReducer = (
  state: RegisterFormState,
  action: RegisterFormAction,
): RegisterFormState => {
  switch (action.type) {
    case "field/change":
      return {
        ...state,
        fields: { ...state.fields, [action.field]: action.value },
        error: null,
      };

    case "submit/start":
      return { ...state, status: "loading", error: null };

    case "submit/error":
      return { ...state, status: "error", error: action.message };

    case "submit/done":
      return { ...state, status: "idle", error: null };

    default:
      return state;
  }
};
