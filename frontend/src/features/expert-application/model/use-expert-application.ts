"use client";

import { useReducer } from "react";
import { submitExpertApplication, type ExpertCatalog } from "@/entities/expert";
import { applicationFormReducer, INITIAL_STATE, isDraftComplete } from "./reducer";
import type { CertificateItem, PersonalFields } from "./types";

const SUBMIT_FAILED = "Не удалось отправить заявку. Попробуйте ещё раз.";

type CertificatePayload = {
  area_code: string;
  object_code: string;
  category: number | null;
  valid_until: string;
  number: string;
};

const buildFormData = (
  fields: PersonalFields | null,
  directions: string[],
  certificates: CertificateItem[],
): FormData => {
  const certificatesPayload: CertificatePayload[] = certificates.map((item) => ({
    area_code: item.areaCode,
    object_code: item.objectCode,
    category: item.category,
    valid_until: item.validUntil,
    number: item.number.trim(),
  }));

  const payload = {
    email: fields ? fields.email.trim() : null,
    password: fields ? fields.password : null,
    full_name: fields ? fields.fullName.trim() : null,
    phone: fields ? fields.phone.trim() : null,
    directions,
    certificates: certificatesPayload,
  };

  const formData = new FormData();
  formData.append("payload", JSON.stringify(payload));

  return formData;
};

export const useExpertApplication = (catalog: ExpertCatalog) => {
  const [state, dispatch] = useReducer(applicationFormReducer, INITIAL_STATE);

  const area = catalog.areas.find((item) => item.code === state.draft.areaCode) ?? null;
  const availableObjects = area
    ? catalog.objects.filter((item) => area.objects.includes(item.code))
    : [];

  const draftComplete = isDraftComplete(state.draft);
  const canSubmit =
    state.directions.length > 0 &&
    state.certificates.length > 0 &&
    state.status !== "loading";

  const changeField = (field: keyof PersonalFields, value: string) =>
    dispatch({ type: "field/change", field, value });

  const toggleDirection = (code: string) => dispatch({ type: "direction/toggle", code });

  const selectArea = (code: string) => dispatch({ type: "draft/area", code });
  const selectObject = (code: string) => dispatch({ type: "draft/object", code });
  const selectCategory = (category: number) => dispatch({ type: "draft/category", category });
  const changeDate = (value: string) => dispatch({ type: "draft/date", value });
  const changeNumber = (value: string) => dispatch({ type: "draft/number", value });

  const addCertificate = () => dispatch({ type: "certificate/add" });
  const removeCertificate = (key: number) => dispatch({ type: "certificate/remove", key });
  const closeSuccess = () => dispatch({ type: "success/close" });

  const submit = async () => {
    if (!canSubmit) return;

    dispatch({ type: "submit/start" });

    try {
      const formData = buildFormData(state.fields, state.directions, state.certificates);
      await submitExpertApplication(formData);
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
    changeField,
    toggleDirection,
    selectArea,
    selectObject,
    selectCategory,
    changeDate,
    changeNumber,
    addCertificate,
    removeCertificate,
    closeSuccess,
    submit,
  };
};
