"use client";

import Link from "next/link";
import { formatServiceCount, type DirectionOption } from "@/entities/service";
import { keepDigits } from "@/shared/lib/text";
import Button from "@/shared/ui/button";
import SelectField from "@/shared/ui/select-field";
import TextField from "@/shared/ui/text-field";
import { useRequestForm } from "../../model/use-request-form";
import styles from "./style.module.scss";

type RequestFormProps = {
  directions: DirectionOption[];
  onDirectionChange?: (id: string) => void;
};

const RequestForm = ({ directions, onDirectionChange }: RequestFormProps) => {
  const {
    state,
    service,
    services,
    needsService,
    selectDirection,
    selectService,
    changeField,
    submit,
    reset,
  } = useRequestForm(directions);

  const handleDirection = (id: string) => {
    selectDirection(id);
    onDirectionChange?.(id);
  };

  if (state.status === "success") {
    return (
      <div className={styles.success}>
        <p className={styles.successTitle}>Заявка отправлена</p>
        <p className={styles.successText}>
          Мы свяжемся с вами в течение рабочего дня.
        </p>
        <Button onClick={reset}>Отправить ещё одну</Button>
      </div>
    );
  }

  return (
    <form
      className={styles.form}
      onSubmit={(event) => {
        event.preventDefault();
        void submit();
      }}
    >
      <SelectField
        label="Направление работ"
        placeholder="Выберите направление"
        required
        value={state.directionId}
        onChange={handleDirection}
        options={directions.map((item) => ({
          value: item.id,
          label: item.title,
          hint: formatServiceCount(item.serviceCount),
          image: item.image,
        }))}
      />

      {needsService && (
        <SelectField
          label="Услуга"
          placeholder="Выберите услугу"
          required
          value={state.serviceId}
          onChange={selectService}
          options={services.map((item) => ({
            value: item.id,
            label: item.label,
          }))}
        />
      )}

      <div className={styles.row}>
        <TextField
          label="Ваше имя"
          required
          placeholder="Иван Иванович"
          maxLength={255}
          value={state.fields.name}
          onChange={(value) => changeField("name", value)}
        />
        <TextField
          label="Телефон"
          required
          type="tel"
          inputMode="tel"
          placeholder="+7 999 000-00-00"
          maxLength={32}
          value={state.fields.telephone}
          onChange={(value) => changeField("telephone", value)}
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
        />
        <TextField
          label="Организация"
          placeholder="ООО «Пример»"
          maxLength={255}
          value={state.fields.companyName}
          onChange={(value) => changeField("companyName", value)}
        />
      </div>

      <TextField
        label="ИНН"
        inputMode="numeric"
        placeholder="10 или 12 цифр"
        maxLength={12}
        value={state.fields.inn}
        onChange={(value) => changeField("inn", keepDigits(value))}
      />

      <TextField
        label="Задача"
        required
        multiline
        placeholder="Что нужно: тип оборудования, год выпуска, есть ли паспорт, сроки"
        maxLength={2000}
        value={state.fields.comment}
        onChange={(value) => changeField("comment", value)}
      />

      {state.error && <p className={styles.error}>{state.error}</p>}

      <Button type="submit" disabled={!service || state.status === "loading"}>
        {state.status === "loading" ? "Отправляем…" : "Отправить заявку"}
      </Button>

      <p className={styles.consent}>
        Нажимая кнопку, вы соглашаетесь с{" "}
        <Link href="/politika-konfidencialnosti" className={styles.consentLink}>
          политикой конфиденциальности
        </Link>
        .
      </p>
    </form>
  );
};

export default RequestForm;
