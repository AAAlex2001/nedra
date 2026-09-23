import type { OrderAction, OrderState } from "./types";

export const INITIAL_STATE: OrderState = {
  objectCode: "kl",
  mode: "hazard",
  hazardClass: null,
  category: null,
  areaCode: "",
  deadline: null,
  files: [],
  companyCard: null,
  comment: "",
  status: "idle",
  error: null,
};

export const orderReducer = (state: OrderState, action: OrderAction): OrderState => {
  switch (action.type) {
    case "object/select":
      return { ...state, objectCode: action.code, areaCode: "", error: null };

    case "mode/set":
      if (action.mode === "unknown") {
        return { ...state, mode: action.mode, hazardClass: null, category: null, error: null };
      }

      return { ...state, mode: action.mode, error: null };

    case "hazard/select":
      return { ...state, hazardClass: action.value, error: null };

    case "category/select":
      return { ...state, category: action.value, error: null };

    case "area/select":
      return { ...state, areaCode: action.code, error: null };

    case "deadline/select":
      return { ...state, deadline: action.value, error: null };

    case "files/add":
      return { ...state, files: [...state.files, ...action.files], error: null };

    case "files/remove":
      return { ...state, files: state.files.filter((file, index) => index !== action.index) };

    case "card/set":
      return { ...state, companyCard: action.file, error: null };

    case "card/remove":
      return { ...state, companyCard: null };

    case "comment/change":
      return { ...state, comment: action.value };

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
