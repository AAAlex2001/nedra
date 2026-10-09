"use client";

import type { ExpertCatalog } from "@/entities/expert";
import { contractKindsFor, createExpertise, type ContractKind } from "@/entities/expertise";
import { orderErrors } from "./order-validation";
import type { OrderState, RequirementMode } from "./types";
import { useOrder } from "./use-order";

const categoryFor = (catalog: ExpertCatalog, state: OrderState): number | null => {
  if (state.mode === "category") return state.category;
  if (state.mode !== "hazard") return null;

  const rule = catalog.hazard_classes.find((item) => item.hazard_class === state.hazardClass);

  return rule ? rule.category : null;
};

export const useExpertiseOrder = (catalog: ExpertCatalog) => {
  const order = useOrder();
  const { state, dispatch } = order;

  const availableAreas = catalog.areas.filter((area) => area.objects.includes(state.objectCode));
  const contractKinds = state.objectCode ? contractKindsFor(state.objectCode) : [];

  const requiredCategory = categoryFor(catalog, state);

  const objectName = state.objectName.trim();
  const allErrors = { ...orderErrors(state, order.price), ...order.customerProblems };
  const hasErrors = Object.keys(allErrors).length > 0;
  const errors = order.attempted ? allErrors : {};

  const selectObject = (code: string) => dispatch({ type: "object/select", code });
  const selectKind = (kind: ContractKind | "") => dispatch({ type: "kind/select", kind });
  const setMode = (mode: RequirementMode) => dispatch({ type: "mode/set", mode });
  const selectHazard = (value: number) => dispatch({ type: "hazard/select", value });
  const selectCategory = (value: number) => dispatch({ type: "category/select", value });
  const selectArea = (code: string) => dispatch({ type: "area/select", code });
  const addFiles = (files: File[]) => dispatch({ type: "files/add", files });
  const removeFile = (index: number) => dispatch({ type: "files/remove", index });

  const submit = async () => {
    order.markAttempted();
    if (hasErrors) return;

    const payload = {
      ...order.payload,
      object_name: objectName,
      contract_kind: state.contractKind || null,
      object_code: state.objectCode || null,
      area_code: state.areaCode || null,
      hazard_class: state.mode === "hazard" ? state.hazardClass : null,
      expert_category: state.mode === "category" ? state.category : null,
    };

    const formData = new FormData();
    formData.append("payload", JSON.stringify(payload));

    for (const file of state.files) {
      formData.append("files", file);
    }

    await order.send(formData, createExpertise);
  };

  return {
    order,
    availableAreas,
    contractKinds,
    requiredCategory,
    errors,
    selectObject,
    selectKind,
    setMode,
    selectHazard,
    selectCategory,
    selectArea,
    addFiles,
    removeFile,
    submit,
  };
};
