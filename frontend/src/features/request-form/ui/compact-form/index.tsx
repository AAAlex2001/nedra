"use client";

import type { DirectionOption } from "@/entities/service";
import Button from "@/shared/ui/button";
import LegalConsents from "@/shared/ui/legal-consents";
import SelectField from "@/shared/ui/select-field";
import TextField from "@/shared/ui/text-field";
import { useRequestForm } from "../../model/use-request-form";
import styles from "./style.module.scss";

type CompactRequestFormProps = {
  directions: DirectionOption[];
};

const CompactRequestForm = ({ directions }: CompactRequestFormProps) => {
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

  if (state.status === "success") {
    return (
      <div className={styles.success}>
        <p className={styles.successTitle}>Заявка отправлена</p>
        <p className={styles.successText}>Мы свяжемся с вами в течение рабочего дня.</p>
        <Button className={styles.submit} onClick={reset}>
          Отправить ещё одну
        </Button>
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
        placeholder="Направление работ"
        required
        compact
        value={state.directionId}
        onChange={selectDirection}
        options={directions.map((item) => ({ value: item.id, label: item.title }))}
      />

      {needsService && (
        <SelectField
          label="Услуга"
          placeholder="Услуга"
          required
          compact
          value={state.serviceId}
          onChange={selectService}
          options={services.map((item) => ({ value: item.id, label: item.label }))}
        />
      )}

      <TextField
        required
        compact
        placeholder="Ваше имя"
        maxLength={255}
        value={state.fields.name}
        onChange={(value) => changeField("name", value)}
      />

      <TextField
        required
        compact
        type="tel"
        inputMode="tel"
        placeholder="Телефон"
        maxLength={32}
        value={state.fields.telephone}
        onChange={(value) => changeField("telephone", value)}
      />

      <TextField
        required
        compact
        type="email"
        inputMode="email"
        placeholder="Email"
        value={state.fields.email}
        onChange={(value) => changeField("email", value)}
      />

      <LegalConsents compact />

      {state.error && <p className={styles.error}>{state.error}</p>}

      <Button
        type="submit"
        className={styles.submit}
        disabled={!service}
        loading={state.status === "loading"}
      >
        Отправить заявку
      </Button>
    </form>
  );
};

export default CompactRequestForm;
