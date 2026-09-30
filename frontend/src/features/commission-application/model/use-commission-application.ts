"use client";

import { useReducer } from "react";
import type { Attestation } from "@/entities/commission";
import type { ExpertCatalog } from "@/entities/expert";
import { submitCommissionApplication } from "../api/submit-application";
import { applicationReducer, INITIAL_STATE, isDraftComplete } from "./reducer";
import type { ContactField } from "./types";

const SUBMIT_FAILED = "Не удалось отправить заявку. Попробуйте ещё раз.";

export const useCommissionApplication = (catalog: ExpertCatalog) => {
  const [state, dispatch] = useReducer(applicationReducer, INITIAL_STATE);

  const area = catalog.areas.find((item) => item.code === state.draft.areaCode) ?? null;
  const availableObjects = area
    ? catalog.objects.filter((item) => area.objects.includes(item.code))
    : [];

  const draftComplete = isDraftComplete(state.draft);
  const contactsFilled =
    state.contacts.fullName.trim().length >= 3 &&
    state.contacts.phone.trim().length >= 5 &&
    state.contacts.email.trim() !== "";
  const canSubmit = contactsFilled && state.items.length > 0 && state.status !== "loading";

  const changeContact = (field: ContactField, value: string) =>
    dispatch({ type: "contact/change", field, value });
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
      await submitCommissionApplication(state.contacts, attestations);
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
    changeContact,
    selectArea,
    selectObject,
    selectCategory,
    addItem,
    removeItem,
    submit,
  };
};
