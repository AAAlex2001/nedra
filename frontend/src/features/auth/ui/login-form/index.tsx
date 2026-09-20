"use client";

import Button from "@/shared/ui/button";
import TextField from "@/shared/ui/text-field";
import { useLoginForm } from "../../model/use-login-form";
import styles from "../form.module.scss";

type LoginFormProps = {
  onSuccess: () => void;
  onSwitchToRegister: () => void;
};

const LoginForm = ({ onSuccess, onSwitchToRegister }: LoginFormProps) => {
  const { state, changeField, submit } = useLoginForm(onSuccess);

  return (
    <form
      className={styles.form}
      onSubmit={(event) => {
        event.preventDefault();
        void submit();
      }}
    >
      <TextField
        label="Email"
        required
        type="email"
        inputMode="email"
        autoComplete="email"
        placeholder="mail@example.com"
        value={state.fields.email}
        onChange={(value) => changeField("email", value)}
      />

      <TextField
        label="Пароль"
        required
        type="password"
        autoComplete="current-password"
        placeholder="Ваш пароль"
        maxLength={72}
        value={state.fields.password}
        onChange={(value) => changeField("password", value)}
      />

      {state.error && <p className={styles.error}>{state.error}</p>}

      <Button type="submit" className={styles.submit} loading={state.status === "loading"}>
        Войти
      </Button>

      <p className={styles.switch}>
        Нет аккаунта?{" "}
        <button type="button" className={styles.switchLink} onClick={onSwitchToRegister}>
          Зарегистрироваться
        </button>
      </p>
    </form>
  );
};

export default LoginForm;
