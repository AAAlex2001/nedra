import type { RequestsAction, RequestsState } from "./types";

export const requestsReducer = (
  state: RequestsState,
  action: RequestsAction,
): RequestsState => {
  switch (action.type) {
    case "refresh/start":
      return { ...state, refreshing: true, error: null };

    case "refresh/success":
      return { ...state, refreshing: false, items: action.items };

    case "refresh/error":
      return { ...state, refreshing: false, error: action.message };

    default:
      return state;
  }
};
