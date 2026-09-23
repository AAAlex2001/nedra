"use client";

import { useState } from "react";
import type { PaymentDocumentKind } from "@/entities/billing";
import Button from "@/shared/ui/button";
import Chip from "@/shared/ui/chip";
import FilesField from "@/shared/ui/files-field";
import styles from "./style.module.scss";

const ACCEPT = ".pdf,.doc,.docx,.jpg,.jpeg,.png";

const KINDS: { value: PaymentDocumentKind; label: string }[] = [
  { value: "payment_order", label: "Платёжное поручение" },
  { value: "guarantee_letter", label: "Гарантийное письмо" },
];

const HINTS: Record<PaymentDocumentKind, string> = {
  payment_order: "Документ из банка, подтверждающий перевод по счёту.",
  guarantee_letter:
    "Если внести предоплату сейчас нечем, приложите гарантийное письмо с обязательством оплатить.",
};

type PaymentProofFormProps = {
  pending: boolean;
  onSubmit: (document: File | null, kind: PaymentDocumentKind) => void;
};

const PaymentProofForm = ({ pending, onSubmit }: PaymentProofFormProps) => {
  const [kind, setKind] = useState<PaymentDocumentKind>("payment_order");
  const [file, setFile] = useState<File | null>(null);

  const setChosen = (files: File[]) => {
    const [chosen] = files;
    if (chosen) setFile(chosen);
  };

  return (
    <div className={styles.form}>
      <span className={styles.label}>Что прикладываете</span>
      <div className={styles.row} role="group" aria-label="Тип документа">
        {KINDS.map((item) => (
          <Chip
            key={item.value}
            active={kind === item.value}
            className={styles.chip}
            onClick={() => setKind(item.value)}
          >
            {item.label}
          </Chip>
        ))}
      </div>

      <FilesField
        label="Документ"
        files={file ? [file] : []}
        accept={ACCEPT}
        hint={HINTS[kind]}
        onAdd={setChosen}
        onRemove={() => setFile(null)}
      />

      <Button
        className={styles.submit}
        disabled={pending}
        loading={pending}
        onClick={() => onSubmit(file, kind)}
      >
        Подтвердить оплату
      </Button>
    </div>
  );
};

export default PaymentProofForm;
