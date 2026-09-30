"use client";

import { useReducer } from "react";
import type { Attestation } from "@/entities/commission";
import type { ExpertCatalog } from "@/entities/expert";
import { submitCommissionApplication } from "../api/submit-application";
import { applicationReducer, INITIAL_STATE, isDraftComplete } from "./reducer";

const SUBMIT_FAILED = "Не удалось отправить заявку. Попробуйте ещё раз.";

export const useCommissionApplication = (catalog: ExpertCatalog) => {
  const [state, dispatch] = useReducer(applicationReducer, INITIAL_STATE);

  const area = catalog.areas.find((item) => item.code === state.draft.areaCode) ?? null;
  const availableObjects = area
    ? catalog.objects.filter((item) => area.objects.includes(item.code))
    : [];

  const draftComplete = isDraftComplete(state.draft);
  const canSubmit =
    state.fullName.trim().length >= 3 && state.items.length > 0 && state.status !== "loading";

  const changeName = (value: string) => dispatch({ type: "name/change", value });
  const selectArea = (code: string) => dispatch({ type: "draft/area", code });
  const selectObject = (code: string) => dispatch({ type: "draft/object", code });
  const selectCategory = (category: number) => dispatch({ type: "draft/category", category });
  const addItem = () => dispatch({ type: "item/add" });
  const removeItem = (key: number) => dispatch({ type: "item/remove", key });

  const submit = async () => {
    if (!canSubmit) return;

    dispatch({ type: "submit/start" });

    const attestations: Attestation[] = state.items.map((item) => ({
      area_code: item.areaCode,
      object_code: item.objectCode,
      category: item.category,
    }));

    try {
      await submitCommissionApplication(state.fullName, attestations);
      dispatch({ type: "submit/success" });
    } catch (error) {
      const message = error instanceof Error && error.message ? error.message : SUBMIT_FAILED;
      dispatch({ type: "submit/error", message });
    }
  };

  return {
    state,
    area,
    availableObjects,
    draftComplete,
    canSubmit,
    changeName,
    selectArea,
    selectObject,
    selectCategory,
    addItem,
    removeItem,
    submit,
  };
};
