"use client";

import { useCallback, useMemo, useReducer } from "react";
import type { DirectionOption } from "@/entities/service";
import { ApiError } from "@/shared/api";
import { createRequest } from "../api/create-request";
import { INITIAL_STATE, requestFormReducer } from "./reducer";
import type { FieldErrors, RequestFields } from "./types";
import { isValid, validate } from "./validation";

export const useRequestForm = (directions: DirectionOption[]) => {
  const [state, dispatch] = useReducer(requestFormReducer, INITIAL_STATE);

  const direction = useMemo(
    () => directions.find((item) => item.id === state.directionId) ?? null,
    [directions, state.directionId],
  );

  // Второй дропдаун нужен только там, где услуг больше одной.
  const needsService = (direction?.services.length ?? 0) > 1;

  const service = useMemo(() => {
    if (!direction) return null;
    if (!needsService) return direction.services[0] ?? null;
    return direction.services.find((item) => item.id === state.serviceId) ?? null;
  }, [direction, needsService, state.serviceId]);

  const errors = useMemo(
    () => validate(state.fields, Boolean(service)),
    [state.fields, service],
  );

  const visibleErrors: FieldErrors = state.submitted ? errors : {};

  const selectDirection = useCallback(
    (id: string) => dispatch({ type: "direction/select", id }),
    [],
  );

  const selectService = useCallback(
    (id: string) => dispatch({ type: "service/select", id }),
    [],
  );

  const changeField = useCallback(
    (field: keyof RequestFields, value: string) =>
      dispatch({ type: "field/change", field, value }),
    [],
  );

  const reset = useCallback(() => dispatch({ type: "form/reset" }), []);

  const submit = useCallback(async () => {
    dispatch({ type: "submit/start" });

    if (!isValid(errors) || !service) {
      dispatch({ type: "submit/error", message: "" });
      return;
    }

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
  }, [errors, service, state.fields]);

  return {
    state,
    direction,
    service,
    needsService,
    errors: visibleErrors,
    selectDirection,
    selectService,
    changeField,
    submit,
    reset,
  };
};
