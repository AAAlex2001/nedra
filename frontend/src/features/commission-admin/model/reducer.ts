import type { CommissionAdminAction, CommissionAdminState } from "./types";

export const commissionAdminReducer = (
  state: CommissionAdminState,
  action: CommissionAdminAction,
): CommissionAdminState => {
  switch (action.type) {
    case "delete/start":
      return { ...state, pendingId: action.id, error: null };

    case "delete/success":
      return {
        ...state,
        pendingId: null,
        items: state.items.filter((item) => item.id !== action.id),
      };

    case "delete/error":
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
