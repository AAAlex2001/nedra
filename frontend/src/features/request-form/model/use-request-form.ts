"use client";

import { useReducer } from "react";
import type { DirectionOption } from "@/entities/service";
import { ApiError } from "@/shared/api";
import { createRequest } from "../api/create-request";
import { INITIAL_STATE, requestFormReducer } from "./reducer";
import type { RequestFields } from "./types";

export const useRequestForm = (directions: DirectionOption[]) => {
  const [state, dispatch] = useReducer(requestFormReducer, INITIAL_STATE);

  const direction =
    directions.find((item) => item.id === state.directionId) ?? null;

  const services = direction?.services ?? [];
  const needsService = services.length > 1;

  const service = needsService
    ? (services.find((item) => item.id === state.serviceId) ?? null)
    : (services[0] ?? null);

  const selectDirection = (id: string) =>
    dispatch({ type: "direction/select", id });

  const selectService = (id: string) => dispatch({ type: "service/select", id });

  const changeField = (field: keyof RequestFields, value: string) =>
    dispatch({ type: "field/change", field, value });

  const reset = () => dispatch({ type: "form/reset" });

  const submit = async () => {
    if (!service) return;

    dispatch({ type: "submit/start" });

    try {
      await createRequest(state.fields, service.activity);
      dispatch({ type: "submit/success" });
    } catch (error) {
      dispatch({
        type: "submit/error",
        message:
          error instanceof ApiError
            ? error.message
            : "Не удалось отправить заявку. Попробуйте ещё раз или позвоните нам.",
      });
    }
  };

  return {
    state,
    direction,
    service,
    services,
    needsService,
    selectDirection,
    selectService,
    changeField,
    submit,
    reset,
  };
};
