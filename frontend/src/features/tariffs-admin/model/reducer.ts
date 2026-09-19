import type { TariffGridAction, TariffGridState } from "./types";

export const tariffGridReducer = (
  state: TariffGridState,
  action: TariffGridAction,
): TariffGridState => {
  switch (action.type) {
    case "cell/change":
      return {
        ...state,
        values: { ...state.values, [action.key]: action.value },
        status: "idle",
        error: null,
      };

    case "save/start":
      return { ...state, status: "saving", error: null };

    case "save/success":
      return { ...state, status: "saved", values: action.values, saved: action.values };

    case "save/error":
      return { ...state, status: "error", error: action.message };

    default:
      return state;
  }
};
