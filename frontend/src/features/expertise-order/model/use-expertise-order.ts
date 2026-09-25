"use client";

import { useEffect, useReducer } from "react";
import type { ExpertCatalog } from "@/entities/expert";
import {
  contractKindsFor,
  createExpertise,
  fetchMyExpertises,
  type ContractKind,
} from "@/entities/expertise";
import { INITIAL_STATE, orderReducer } from "./reducer";
import type { CompanyField, Deadline, RequirementMode } from "./types";

const SUBMIT_FAILED = "Не удалось отправить заявку. Попробуйте ещё раз.";

const OPTIONAL_COMPANY_FIELDS: CompanyField[] = ["kpp"];

export const useExpertiseOrder = (catalog: ExpertCatalog) => {
  const [state, dispatch] = useReducer(orderReducer, INITIAL_STATE);

  useEffect(() => {
    const fillFromLastOrder = async () => {
      try {
        const items = await fetchMyExpertises();
        const last = items.find((item) => item.company !== null);
        if (last?.company) dispatch({ type: "company/fill", company: last.company });
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

  const companyFilled = Object.entries(state.company).every(
    ([field, value]) =>
      OPTIONAL_COMPANY_FIELDS.includes(field as CompanyField) || value.trim() !== "",
  );

  const canSubmit =
    state.files.length > 0 &&
    state.objectName.trim() !== "" &&
    companyFilled &&
    state.status !== "loading";

  const selectObject = (code: string) => dispatch({ type: "object/select", code });
  const selectKind = (kind: ContractKind | "") => dispatch({ type: "kind/select", kind });
  const changeObjectName = (value: string) => dispatch({ type: "objectName/change", value });
  const setMode = (mode: RequirementMode) => dispatch({ type: "mode/set", mode });
  const selectHazard = (value: number) => dispatch({ type: "hazard/select", value });
  const selectCategory = (value: number) => dispatch({ type: "category/select", value });
  const selectArea = (code: string) => dispatch({ type: "area/select", code });
  const selectDeadline = (value: Deadline) => dispatch({ type: "deadline/select", value });
  const changeCompany = (field: CompanyField, value: string) =>
    dispatch({ type: "company/change", field, value });
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

    const company = { ...state.company, kpp: state.company.kpp.trim() || null };

    const payload = {
      object_name: state.objectName.trim(),
      company,
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

    if (state.companyCard) {
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
    changeCompany,
    addFiles,
    removeFile,
    setCard,
    removeCard,
    changeComment,
    closeSuccess,
    submit,
  };
};
