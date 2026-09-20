"use client";

import { useReducer } from "react";
import { registerUser, useSession, type UserRole } from "@/entities/user";
import { describeError } from "./describe-error";
import { INITIAL_REGISTER, registerReducer } from "./register-reducer";
import type { RegisterFields } from "./types";

const REGISTER_FAILED = "Не удалось зарегистрироваться. Попробуйте ещё раз.";

export const useRegisterForm = (onSuccess: () => void) => {
  const session = useSession();
  const [state, dispatch] = useReducer(registerReducer, INITIAL_REGISTER);

  const selectRole = (role: UserRole) => dispatch({ type: "role/select", role });

  const changeField = (field: keyof RegisterFields, value: string) =>
    dispatch({ type: "field/change", field, value });

  const submit = async () => {
    dispatch({ type: "submit/start" });

    try {
      const user = await registerUser({
        full_name: state.fields.fullName.trim(),
        email: state.fields.email.trim(),
        phone: state.fields.phone.trim(),
        password: state.fields.password,
        role: state.role,
      });

      session.signIn(user);
      dispatch({ type: "submit/done" });
      onSuccess();
    } catch (error) {
      dispatch({ type: "submit/error", message: describeError(error, REGISTER_FAILED) });
    }
  };

  return { state, selectRole, changeField, submit };
};
