"use client";

import { useReducer } from "react";
import type { ExpertCatalog } from "@/entities/expert";
import { createExpertise } from "@/entities/expertise";
import { INITIAL_STATE, orderReducer } from "./reducer";
import type { RequirementMode } from "./types";

const SUBMIT_FAILED = "Не удалось отправить заявку. Попробуйте ещё раз.";

export const useExpertiseOrder = (catalog: ExpertCatalog) => {
  const [state, dispatch] = useReducer(orderReducer, INITIAL_STATE);

  const currentObject = catalog.objects.find((object) => object.code === state.objectCode);
  const availableAreas = catalog.areas.filter((area) => area.objects.includes(state.objectCode));
  const selectedArea = availableAreas.find((area) => area.code === state.areaCode) ?? null;

  const hazardRule = catalog.hazard_classes.find(
    (rule) => rule.hazard_class === state.hazardClass,
  );
  const requiredCategory = state.mode === "hazard" ? (hazardRule?.category ?? null) : state.category;

  const canSubmit =
    selectedArea !== null &&
    requiredCategory !== null &&
    state.files.length > 0 &&
    state.status !== "loading";

  const selectObject = (code: string) => dispatch({ type: "object/select", code });
  const setMode = (mode: RequirementMode) => dispatch({ type: "mode/set", mode });
  const selectHazard = (value: number) => dispatch({ type: "hazard/select", value });
  const selectCategory = (value: number) => dispatch({ type: "category/select", value });
  const selectArea = (code: string) => dispatch({ type: "area/select", code });
  const addFiles = (files: File[]) => dispatch({ type: "files/add", files });
  const removeFile = (index: number) => dispatch({ type: "files/remove", index });
  const changeComment = (value: string) => dispatch({ type: "comment/change", value });
  const closeSuccess = () => dispatch({ type: "success/close" });

  const submit = async () => {
    if (!canSubmit) return;

    dispatch({ type: "submit/start" });

    const payload = {
      object_code: state.objectCode,
      area_code: state.areaCode,
      hazard_class: state.mode === "hazard" ? state.hazardClass : null,
      expert_category: state.mode === "category" ? state.category : null,
      comment: state.comment.trim() || null,
    };

    const formData = new FormData();
    formData.append("payload", JSON.stringify(payload));
    for (const file of state.files) {
      formData.append("files", file);
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
    requiredCategory,
    canSubmit,
    selectObject,
    setMode,
    selectHazard,
    selectCategory,
    selectArea,
    addFiles,
    removeFile,
    changeComment,
    closeSuccess,
    submit,
  };
};
