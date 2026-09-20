import type { LoginFormAction, LoginFormState } from "./types";

export const INITIAL_LOGIN: LoginFormState = {
  fields: { email: "", password: "" },
  status: "idle",
  error: null,
};

export const loginReducer = (
  state: LoginFormState,
  action: LoginFormAction,
): LoginFormState => {
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
