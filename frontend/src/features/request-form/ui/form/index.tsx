"use client";

import Link from "next/link";
import { useEffect } from "react";
import type { DirectionOption } from "@/entities/service";
import { formatServiceCount } from "@/entities/service";
import { useRequestForm } from "../../model/use-request-form";
import Select from "../select";
import TextField from "../text-field";
import styles from "./style.module.scss";

type RequestFormProps = {
  directions: DirectionOption[];
  onDirectionChange?: (direction: DirectionOption | null) => void;
};

const RequestForm = ({ directions, onDirectionChange }: RequestFormProps) => {
  const {
    state,
    direction,
    needsService,
    errors,
    selectDirection,
    selectService,
    changeField,
    submit,
    reset,
  } = useRequestForm(directions);

  useEffect(() => {
    onDirectionChange?.(direction);
  }, [direction, onDirectionChange]);

  if (state.status === "success") {
    return (
      <div className={styles.success}>
        <h3 className={styles.successTitle}>Заявка отправлена</h3>
        <p className={styles.successText}>
          Мы свяжемся с вами в течение рабочего дня.
        </p>
        <button type="button" className={styles.submit} onClick={reset}>
          Отправить ещё одну
        </button>
      </div>
    );
  }

  return (
    <form
      className={styles.form}
      noValidate
      onSubmit={(event) => {
        event.preventDefault();
        void submit();
      }}
    >
      <Select
        label="Направление работ"
        placeholder="Выберите направление"
        options={directions.map((item) => ({
          id: item.id,
          title: item.title,
          subtitle: formatServiceCount(item.serviceCount),
          image: item.image,
        }))}
        value={state.directionId}
        onChange={selectDirection}
        required
        invalid={Boolean(errors.service) && !direction}
      />

      {needsService && direction && (
        <Select
          label="Услуга"
          placeholder="Выберите услугу"
          options={direction.services.map((item) => ({
            id: item.id,
            title: item.label,
          }))}
          value={state.serviceId}
          onChange={selectService}
          required
          invalid={Boolean(errors.service)}
        />
      )}

      <div className={styles.row}>
        <TextField
          label="Ваше имя"
          required
          placeholder="Иван Иванович"
          value={state.fields.name}
          onChange={(value) => changeField("name", value)}
          error={errors.name}
          maxLength={255}
        />
        <TextField
          label="Телефон"
          required
          type="tel"
          inputMode="tel"
          placeholder="+7 999 000-00-00"
          value={state.fields.telephone}
          onChange={(value) => changeField("telephone", value)}
          error={errors.telephone}
          maxLength={32}
        />
      </div>

      <div className={styles.row}>
        <TextField
          label="Email"
          required
          type="email"
          inputMode="email"
          placeholder="mail@example.com"
          value={state.fields.email}
          onChange={(value) => changeField("email", value)}
          error={errors.email}
        />
        <TextField
          label="Организация"
          placeholder="ООО «Пример»"
          value={state.fields.companyName}
          onChange={(value) => changeField("companyName", value)}
          maxLength={255}
        />
      </div>

      <div className={styles.row}>
        <TextField
          label="ИНН"
          inputMode="numeric"
          placeholder="10 или 12 цифр"
          value={state.fields.inn}
          onChange={(value) => changeField("inn", value.replace(/\D/g, ""))}
          error={errors.inn}
          maxLength={12}
        />
        <span className={styles.spacer} aria-hidden />
      </div>

      <TextField
        label="Задача"
        required
        multiline
        placeholder="Что нужно: тип оборудования, год выпуска, есть ли паспорт, сроки"
        value={state.fields.comment}
        onChange={(value) => changeField("comment", value)}
        error={errors.comment}
        maxLength={2000}
      />

      {state.error && <p className={styles.formError}>{state.error}</p>}

      <button
        type="submit"
        className={styles.submit}
        disabled={state.status === "loading"}
      >
        {state.status === "loading" ? "Отправляем…" : "Отправить заявку"}
      </button>

      <p className={styles.consent}>
        Нажимая кнопку, вы соглашаетесь с{" "}
        <Link href="/politika-konfidencialnosti" className={styles.consentLink}>
          политикой конфиденциальности
        </Link>{" "}
        и обработкой персональных данных.
      </p>
    </form>
  );
};

export default RequestForm;
