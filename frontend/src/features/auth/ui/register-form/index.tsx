"use client";

import Link from "next/link";
import Button from "@/shared/ui/button";
import TextField from "@/shared/ui/text-field";
import { useRegisterForm } from "../../model/use-register-form";
import RoleSelect from "../role-select";
import styles from "../form.module.scss";

const PASSWORD_MIN_LENGTH = 8;
const EXPERT_APPLICATION_PATH = "/registratsiya-eksperta";

type RegisterFormProps = {
  onSuccess: () => void;
  onSwitchToLogin: () => void;
  onClose: () => void;
};

const RegisterForm = ({ onSuccess, onSwitchToLogin, onClose }: RegisterFormProps) => {
  const { state, selectRole, changeField, submit } = useRegisterForm(onSuccess);

  return (
    <form
      className={styles.form}
      onSubmit={(event) => {
        event.preventDefault();
        void submit();
      }}
    >
      <RoleSelect value={state.role} onChange={selectRole} />

      {state.role === "expert" ? (
        <div className={styles.notice}>
          <p className={styles.noticeTitle}>Эксперты проходят проверку</p>
          <p className={styles.noticeText}>
            Заполните заявку с областями аттестации и удостоверениями. Мы проверим
            документы и откроем доступ в кабинет, обычно это занимает до двух рабочих дней.
          </p>
          <Button href={EXPERT_APPLICATION_PATH} className={styles.submit} onClick={onClose}>
            Заполнить заявку эксперта
          </Button>
        </div>
      ) : (
        <>
          <TextField
            label="Имя и фамилия"
            required
            autoComplete="name"
            placeholder="Иван Иванов"
            minLength={2}
            maxLength={255}
            value={state.fields.fullName}
            onChange={(value) => changeField("fullName", value)}
          />

          <div className={styles.row}>
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
              label="Телефон"
              required
              type="tel"
              inputMode="tel"
              autoComplete="tel"
              placeholder="+7 999 000-00-00"
              minLength={10}
              maxLength={32}
              value={state.fields.phone}
              onChange={(value) => changeField("phone", value)}
            />
          </div>

          <TextField
            label="Пароль"
            required
            type="password"
            autoComplete="new-password"
            placeholder="Не короче 8 символов"
            minLength={PASSWORD_MIN_LENGTH}
            maxLength={72}
            value={state.fields.password}
            onChange={(value) => changeField("password", value)}
          />
          <p className={styles.hint}>Минимум 8 символов, хотя бы одна буква и одна цифра.</p>

          {state.error && <p className={styles.error}>{state.error}</p>}

          <Button type="submit" className={styles.submit} loading={state.status === "loading"}>
            Зарегистрироваться
          </Button>

          <p className={styles.consent}>
            Нажимая кнопку, вы соглашаетесь с{" "}
            <Link href="/politika-konfidencialnosti" className={styles.consentLink}>
              политикой конфиденциальности
            </Link>
            .
          </p>
        </>
      )}

      <p className={styles.switch}>
        Уже есть аккаунт?{" "}
        <button type="button" className={styles.switchLink} onClick={onSwitchToLogin}>
          Войти
        </button>
      </p>
    </form>
  );
};

export default RegisterForm;
