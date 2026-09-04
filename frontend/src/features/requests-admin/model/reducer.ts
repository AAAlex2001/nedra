import type { RequestsAction, RequestsState } from "./types";

export const requestsReducer = (
  state: RequestsState,
  action: RequestsAction,
): RequestsState => {
  switch (action.type) {
    case "delete/start":
      return { ...state, pendingId: action.id, error: null };

    case "delete/success":
      return {
        ...state,
        pendingId: null,
        items: state.items.filter((item) => item.request_id !== action.id),
      };

    case "delete/error":
      return { ...state, pendingId: null, error: action.message };

    case "refresh/start":
      return { ...state, refreshing: true, error: null };

    case "refresh/success":
      return { ...state, refreshing: false, items: action.items };

    case "refresh/error":
      return { ...state, refreshing: false, error: action.message };

    case "error/clear":
      return { ...state, error: null };

    default:
      return state;
  }
};
