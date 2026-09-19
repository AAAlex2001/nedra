import type { ApplicationsAction, ApplicationsState } from "./types";

export const applicationsReducer = (
  state: ApplicationsState,
  action: ApplicationsAction,
): ApplicationsState => {
  switch (action.type) {
    case "filter/set":
      return { ...state, filter: action.filter };

    case "review/start":
      return { ...state, pendingId: action.id, error: null };

    case "review/success":
      return {
        ...state,
        pendingId: null,
        items: state.items.map((item) => (item.id === action.item.id ? action.item : item)),
      };

    case "review/error":
      return { ...state, pendingId: null, error: action.message };

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
