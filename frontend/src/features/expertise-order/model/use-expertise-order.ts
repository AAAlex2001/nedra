"use client";

import type { ExpertCatalog } from "@/entities/expert";
import { contractKindsFor, createExpertise, type ContractKind } from "@/entities/expertise";
import { filesErrors, objectErrors, priceErrors } from "./order-validation";
import type { OrderState, RequirementMode } from "./types";
import { useOrder } from "./use-order";
import { useSteps, type OrderStep } from "./use-steps";

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

  const stepList: OrderStep[] = [
    { key: "object", title: "Объект экспертизы", errors: objectErrors(state) },
    { key: "requirements", title: "Требования к эксперту", errors: {} },
    { key: "terms", title: "Срок и цена", errors: priceErrors(order.price) },
    { key: "files", title: "Документация", errors: filesErrors(state) },
    { key: "customer", title: "Заказчик", errors: order.customerProblems },
    { key: "comment", title: "Комментарий", errors: {} },
  ];
  const steps = useSteps(stepList);

  const selectObject = (code: string) => dispatch({ type: "object/select", code });
  const selectKind = (kind: ContractKind | "") => dispatch({ type: "kind/select", kind });
  const setMode = (mode: RequirementMode) => dispatch({ type: "mode/set", mode });
  const selectHazard = (value: number) => dispatch({ type: "hazard/select", value });
  const selectCategory = (value: number) => dispatch({ type: "category/select", value });
  const selectArea = (code: string) => dispatch({ type: "area/select", code });
  const addFiles = (files: File[]) => dispatch({ type: "files/add", files });
  const removeFile = (index: number) => dispatch({ type: "files/remove", index });

  const submit = async () => {
    if (!steps.validate()) return;

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

    const sent = await order.send(formData, createExpertise);

    if (sent) steps.reset();
  };

  return {
    order,
    steps,
    availableAreas,
    contractKinds,
    requiredCategory,
    errors: steps.errors,
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
