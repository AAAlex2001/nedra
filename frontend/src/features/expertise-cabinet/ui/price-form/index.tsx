"use client";

import { useState } from "react";
import { MIN_AUDIT_PRICE } from "@/entities/expertise";
import { formatRub } from "@/shared/lib/money";
import { keepDigits } from "@/shared/lib/text";
import Button from "@/shared/ui/button";
import TextField from "@/shared/ui/text-field";
import styles from "./style.module.scss";

type PriceFormProps = {
  label: string;
  submitText: string;
  pending: boolean;
  below?: number;
  onSubmit: (price: number) => void;
};

const PriceForm = ({ label, submitText, pending, below, onSubmit }: PriceFormProps) => {
  const [value, setValue] = useState("");

  const price = Number(value);
  const tooLow = value !== "" && price < MIN_AUDIT_PRICE;
  const tooHigh = below !== undefined && value !== "" && price >= below;
  const valid = value !== "" && !tooLow && !tooHigh;

  return (
    <div className={styles.form}>
      <TextField
        label={label}
        inputMode="numeric"
        placeholder="Не менее 100 000"
        maxLength={10}
        value={value}
        onChange={(text) => setValue(keepDigits(text))}
      />

      {tooLow && <p className={styles.error}>Стоимость аудита — не менее 100 000 ₽</p>}
      {tooHigh && below !== undefined && (
        <p className={styles.error}>Предложите цену ниже {formatRub(below)}</p>
      )}

      <Button disabled={!valid} loading={pending} onClick={() => onSubmit(price)}>
        {submitText}
      </Button>
    </div>
  );
};

export default PriceForm;
