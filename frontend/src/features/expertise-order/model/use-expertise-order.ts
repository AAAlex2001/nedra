"use client";

import { useEffect, useReducer } from "react";
import type { ExpertCatalog } from "@/entities/expert";
import {
  contractKindsFor,
  createExpertise,
  fetchMyExpertises,
  type ContractKind,
  type CustomerType,
} from "@/entities/expertise";
import { INITIAL_STATE, orderReducer } from "./reducer";
import type { CompanyField, Deadline, IndividualField, RequirementMode } from "./types";

const SUBMIT_FAILED = "Не удалось отправить заявку. Попробуйте ещё раз.";

const OPTIONAL_COMPANY_FIELDS: CompanyField[] = ["kpp"];

const parsePrice = (value: string): number => Number(value.replace(/\s/g, "").replace(",", "."));

const allFilled = (fields: Record<string, string>, optional: string[] = []): boolean =>
  Object.entries(fields).every(([field, value]) => optional.includes(field) || value.trim() !== "");

export const useExpertiseOrder = (catalog: ExpertCatalog) => {
  const [state, dispatch] = useReducer(orderReducer, INITIAL_STATE);

  useEffect(() => {
    const fillFromLastOrder = async () => {
      try {
        const items = await fetchMyExpertises();
        const lastCompany = items.find((item) => item.company !== null)?.company;
        const lastIndividual = items.find((item) => item.individual !== null)?.individual;

        if (lastCompany) dispatch({ type: "company/fill", company: lastCompany });
        if (lastIndividual) dispatch({ type: "individual/fill", individual: lastIndividual });
        if (items[0]) dispatch({ type: "customer/select", customerType: items[0].customer_type });
      } catch {
        return;
      }
    };

    void fillFromLastOrder();
  }, []);

  const currentObject = catalog.objects.find((object) => object.code === state.objectCode);
  const availableAreas = catalog.areas.filter((area) => area.objects.includes(state.objectCode));
  const selectedArea = availableAreas.find((area) => area.code === state.areaCode) ?? null;
  const contractKinds = state.objectCode ? contractKindsFor(state.objectCode) : [];

  const hazardRule = catalog.hazard_classes.find(
    (rule) => rule.hazard_class === state.hazardClass,
  );

  let requiredCategory: number | null = null;
  if (state.mode === "hazard") requiredCategory = hazardRule?.category ?? null;
  if (state.mode === "category") requiredCategory = state.category;

  const price = parsePrice(state.price);
  const legal = state.customerType === "legal";
  const customerFilled = legal
    ? allFilled(state.company, OPTIONAL_COMPANY_FIELDS)
    : allFilled(state.individual);

  const canSubmit =
    state.files.length > 0 &&
    state.objectName.trim() !== "" &&
    price > 0 &&
    customerFilled &&
    state.status !== "loading";

  const selectObject = (code: string) => dispatch({ type: "object/select", code });
  const selectKind = (kind: ContractKind | "") => dispatch({ type: "kind/select", kind });
  const changeObjectName = (value: string) => dispatch({ type: "objectName/change", value });
  const setMode = (mode: RequirementMode) => dispatch({ type: "mode/set", mode });
  const selectHazard = (value: number) => dispatch({ type: "hazard/select", value });
  const selectCategory = (value: number) => dispatch({ type: "category/select", value });
  const selectArea = (code: string) => dispatch({ type: "area/select", code });
  const selectDeadline = (value: Deadline) => dispatch({ type: "deadline/select", value });
  const changePrice = (value: string) => dispatch({ type: "price/change", value });
  const selectCustomerType = (customerType: CustomerType) =>
    dispatch({ type: "customer/select", customerType });
  const changeCompany = (field: CompanyField, value: string) =>
    dispatch({ type: "company/change", field, value });
  const changeIndividual = (field: IndividualField, value: string) =>
    dispatch({ type: "individual/change", field, value });
  const addFiles = (files: File[]) => dispatch({ type: "files/add", files });
  const removeFile = (index: number) => dispatch({ type: "files/remove", index });
  const removeCard = () => dispatch({ type: "card/remove" });
  const changeComment = (value: string) => dispatch({ type: "comment/change", value });
  const closeSuccess = () => dispatch({ type: "success/close" });

  const setCard = (files: File[]) => {
    const [file] = files;
    if (file) dispatch({ type: "card/set", file });
  };

  const submit = async () => {
    if (!canSubmit) return;

    dispatch({ type: "submit/start" });

    const company = legal ? { ...state.company, kpp: state.company.kpp.trim() || null } : null;
    const individual = legal ? null : state.individual;

    const payload = {
      object_name: state.objectName.trim(),
      price,
      customer_type: state.customerType,
      company,
      individual,
      contract_kind: state.contractKind || null,
      object_code: state.objectCode || null,
      area_code: state.areaCode || null,
      hazard_class: state.mode === "hazard" ? state.hazardClass : null,
      expert_category: state.mode === "category" ? state.category : null,
      deadline: state.deadline,
      comment: state.comment.trim() || null,
    };

    const formData = new FormData();
    formData.append("payload", JSON.stringify(payload));
    for (const file of state.files) {
      formData.append("files", file);
    }

    if (legal && state.companyCard) {
      formData.append("company_card", state.companyCard);
    }

    try {
      await createExpertise(formData);
      dispatch({ type: "submit/success" });
    } catch (error) {
      const message = error instanceof Error && error.message ? error.message : SUBMIT_FAILED;
      dispatch({ type: "submit/error", message });
    }
  };

  return {
    state,
    currentObject,
    availableAreas,
    selectedArea,
    contractKinds,
    requiredCategory,
    canSubmit,
    selectObject,
    selectKind,
    changeObjectName,
    setMode,
    selectHazard,
    selectCategory,
    selectArea,
    selectDeadline,
    changePrice,
    selectCustomerType,
    changeCompany,
    changeIndividual,
    addFiles,
    removeFile,
    setCard,
    removeCard,
    changeComment,
    closeSuccess,
    submit,
  };
};
