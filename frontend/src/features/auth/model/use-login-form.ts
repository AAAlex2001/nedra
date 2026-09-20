"use client";

import { useReducer } from "react";
import { loginUser, useSession } from "@/entities/user";
import { describeError } from "./describe-error";
import { INITIAL_LOGIN, loginReducer } from "./login-reducer";
import type { LoginFields } from "./types";

const LOGIN_FAILED = "Не удалось войти. Попробуйте ещё раз.";

export const useLoginForm = (onSuccess: () => void) => {
  const session = useSession();
  const [state, dispatch] = useReducer(loginReducer, INITIAL_LOGIN);

  const changeField = (field: keyof LoginFields, value: string) =>
    dispatch({ type: "field/change", field, value });

  const submit = async () => {
    dispatch({ type: "submit/start" });

    try {
      const user = await loginUser({
        email: state.fields.email.trim(),
        password: state.fields.password,
      });

      session.signIn(user);
      dispatch({ type: "submit/done" });
      onSuccess();
    } catch (error) {
      dispatch({ type: "submit/error", message: describeError(error, LOGIN_FAILED) });
    }
  };

  return { state, changeField, submit };
};
