import type { CompanyFields, IndividualFields, OrderAction, OrderState } from "./types";

export const EMPTY_COMPANY: CompanyFields = {
  full_name: "",
  name: "",
  inn: "",
  kpp: "",
  ogrn: "",
  address: "",
  bank: "",
  bic: "",
  account: "",
  corr_account: "",
  signer_position: "",
  signer_name: "",
  signer_genitive: "",
  signer_basis: "Устава",
};

export const EMPTY_INDIVIDUAL: IndividualFields = {
  full_name: "",
  passport_number: "",
  passport_issued_by: "",
  passport_issued_at: "",
  address: "",
};

export const INITIAL_STATE: OrderState = {
  objectCode: "kl",
  contractKind: "",
  objectName: "",
  mode: "hazard",
  hazardClass: null,
  category: null,
  areaCode: "",
  deadline: null,
  price: "",
  customerType: "legal",
  company: EMPTY_COMPANY,
  individual: EMPTY_INDIVIDUAL,
  files: [],
  auditFiles: [],
  companyCard: null,
  comment: "",
  status: "idle",
  error: null,
};

const isUntouched = (fields: Record<string, string>, empty: Record<string, string>): boolean =>
  Object.entries(fields).every(([field, value]) => value === empty[field]);

export const orderReducer = (state: OrderState, action: OrderAction): OrderState => {
  switch (action.type) {
    case "object/select":
      return { ...state, objectCode: action.code, contractKind: "", areaCode: "", error: null };

    case "kind/select":
      return { ...state, contractKind: action.kind, error: null };

    case "objectName/change":
      return { ...state, objectName: action.value, error: null };

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

    case "price/change":
      return { ...state, price: action.value, error: null };

    case "customer/select":
      return { ...state, customerType: action.customerType, error: null };

    case "company/change":
      return {
        ...state,
        company: { ...state.company, [action.field]: action.value },
        error: null,
      };

    case "company/fill":
      if (!isUntouched(state.company, EMPTY_COMPANY)) return state;

      return { ...state, company: { ...action.company, kpp: action.company.kpp ?? "" } };

    case "individual/change":
      return {
        ...state,
        individual: { ...state.individual, [action.field]: action.value },
        error: null,
      };

    case "individual/fill":
      if (!isUntouched(state.individual, EMPTY_INDIVIDUAL)) return state;

      return { ...state, individual: action.individual };

    case "files/add":
      return { ...state, files: [...state.files, ...action.files], error: null };

    case "files/remove":
      return { ...state, files: state.files.filter((file, index) => index !== action.index) };

    case "auditFiles/add": {
      const added = action.files.map((file) => ({ item: action.item, file }));

      return { ...state, auditFiles: [...state.auditFiles, ...added], error: null };
    }

    case "auditFiles/remove":
      return {
        ...state,
        auditFiles: state.auditFiles.filter((entry) => entry !== action.target),
      };

    case "card/set":
      return { ...state, companyCard: action.file, error: null };

    case "card/remove":
      return { ...state, companyCard: null };

    case "comment/change":
      return { ...state, comment: action.value };

    case "submit/start":
      return { ...state, status: "loading", error: null };

    case "submit/success":
      return {
        ...INITIAL_STATE,
        customerType: state.customerType,
        company: state.company,
        individual: state.individual,
        status: "success",
      };

    case "submit/error":
      return { ...state, status: "error", error: action.message };

    case "success/close":
      return { ...state, status: "idle" };

    default:
      return state;
  }
};
