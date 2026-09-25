"use client";

import { useState } from "react";
import type { PaymentDocumentKind } from "@/entities/billing";
import Button from "@/shared/ui/button";
import FilesField from "@/shared/ui/files-field";
import styles from "./style.module.scss";

const ACCEPT = ".pdf,.doc,.docx,.jpg,.jpeg,.png";

const TEXTS: Record<PaymentDocumentKind, { label: string; hint: string; submit: string }> = {
  payment_order: {
    label: "Платёжное поручение",
    hint: "Документ из банка, подтверждающий перевод по счёту. Можно не прикладывать — администратор проверит поступление сам.",
    submit: "Подтвердить оплату",
  },
  guarantee_letter: {
    label: "Гарантийное письмо",
    hint: "Если внести предоплату сейчас нечем, приложите письмо с обязательством оплатить.",
    submit: "Отправить письмо",
  },
};

type PaymentProofFormProps = {
  kind: PaymentDocumentKind;
  pending: boolean;
  onSubmit: (document: File | null) => void;
};

const PaymentProofForm = ({ kind, pending, onSubmit }: PaymentProofFormProps) => {
  const [file, setFile] = useState<File | null>(null);
  const texts = TEXTS[kind];
  const fileRequired = kind === "guarantee_letter";

  const setChosen = (files: File[]) => {
    const [chosen] = files;
    if (chosen) setFile(chosen);
  };

  return (
    <div className={styles.form}>
      <FilesField
        label={texts.label}
        required={fileRequired}
        files={file ? [file] : []}
        accept={ACCEPT}
        hint={texts.hint}
        onAdd={setChosen}
        onRemove={() => setFile(null)}
      />

      <Button
        className={styles.submit}
        disabled={pending || (fileRequired && file === null)}
        loading={pending}
        onClick={() => onSubmit(file)}
      >
        {texts.submit}
      </Button>
    </div>
  );
};

export default PaymentProofForm;
