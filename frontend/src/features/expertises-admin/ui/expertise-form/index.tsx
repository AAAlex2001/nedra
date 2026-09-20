"use client";

import { useState } from "react";
import { EXPERTISE_STATUS_LABELS, type ExpertiseStatus } from "@/entities/expertise";
import { keepDigits } from "@/shared/lib/text";
import Button from "@/shared/ui/button";
import SelectField from "@/shared/ui/select-field";
import TextField from "@/shared/ui/text-field";
import styles from "./style.module.scss";

type ExpertiseFormProps = {
  status: ExpertiseStatus;
  price: string | null;
  pending: boolean;
  onSave: (status: ExpertiseStatus, price: string | null) => void;
  onCancel: () => void;
};

const STATUSES = Object.keys(EXPERTISE_STATUS_LABELS) as ExpertiseStatus[];

const toWhole = (price: string | null): string =>
  price === null ? "" : String(Math.round(Number(price)));

const ExpertiseForm = ({ status, price, pending, onSave, onCancel }: ExpertiseFormProps) => {
  const [draftStatus, setDraftStatus] = useState(status);
  const [draftPrice, setDraftPrice] = useState(toWhole(price));

  const selectStatus = (value: string) => {
    const found = STATUSES.find((item) => item === value);

    if (found) setDraftStatus(found);
  };

  const save = () => onSave(draftStatus, draftPrice === "" ? null : draftPrice);

  return (
    <div className={styles.form}>
      <div className={styles.fields}>
        <SelectField
          label="Статус"
          placeholder="Выберите статус"
          value={draftStatus}
          onChange={selectStatus}
          options={STATUSES.map((item) => ({
            value: item,
            label: EXPERTISE_STATUS_LABELS[item],
          }))}
        />
        <TextField
          label="Стоимость, ₽"
          inputMode="numeric"
          placeholder="не задана"
          value={draftPrice}
          onChange={(value) => setDraftPrice(keepDigits(value))}
        />
      </div>

      <div className={styles.buttons}>
        <button type="button" className={styles.cancel} disabled={pending} onClick={onCancel}>
          Отмена
        </button>
        <Button loading={pending} onClick={save}>
          Сохранить
        </Button>
      </div>
    </div>
  );
};

export default ExpertiseForm;
