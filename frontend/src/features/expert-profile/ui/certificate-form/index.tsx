"use client";

import { useState } from "react";
import type { Certificate, CertificateInput, ExpertCatalog } from "@/entities/expert";
import Button from "@/shared/ui/button";
import Chip from "@/shared/ui/chip";
import OutlineButton from "@/shared/ui/outline-button";
import TextField from "@/shared/ui/text-field";
import styles from "./style.module.scss";

type CertificateFormProps = {
  catalog: ExpertCatalog;
  initial: Certificate | null;
  pending: boolean;
  error: string | null;
  onSubmit: (input: CertificateInput) => void;
  onCancel: () => void;
};

const CertificateForm = ({
  catalog,
  initial,
  pending,
  error,
  onSubmit,
  onCancel,
}: CertificateFormProps) => {
  const [areaCode, setAreaCode] = useState(initial?.area_code ?? "");
  const [objectCode, setObjectCode] = useState(initial?.object_code ?? "");
  const [category, setCategory] = useState<number | null>(initial?.category ?? null);
  const [validUntil, setValidUntil] = useState(initial?.valid_until ?? "");
  const [number, setNumber] = useState(initial?.number ?? "");

  const area = catalog.areas.find((item) => item.code === areaCode) ?? null;
  const complete =
    areaCode !== "" &&
    objectCode !== "" &&
    category !== null &&
    validUntil !== "" &&
    number.trim() !== "";

  const selectArea = (code: string) => {
    setAreaCode(code);

    const next = catalog.areas.find((item) => item.code === code);
    if (next && !next.objects.includes(objectCode)) setObjectCode("");
  };

  const submit = () => {
    if (!complete || category === null) return;

    onSubmit({
      area_code: areaCode,
      object_code: objectCode,
      category,
      valid_until: validUntil,
      number: number.trim(),
    });
  };

  return (
    <div className={styles.form}>
      <p className={styles.heading}>{initial ? "Изменение удостоверения" : "Новое удостоверение"}</p>

      <div className={styles.group}>
        <span className={styles.label}>Область аттестации</span>
        <div className={styles.chips} role="group" aria-label="Область аттестации">
          {catalog.areas.map((item) => (
            <Chip
              key={item.code}
              active={areaCode === item.code}
              title={item.title}
              onClick={() => selectArea(item.code)}
            >
              {item.code}
            </Chip>
          ))}
        </div>
        {area && <p className={styles.note}>{area.title}</p>}
      </div>

      <div className={styles.group}>
        <span className={styles.label}>Объект экспертизы</span>
        <div className={styles.chips} role="group" aria-label="Объект экспертизы">
          {catalog.objects.map((item) => (
            <Chip
              key={item.code}
              active={objectCode === item.code}
              disabled={!area || !area.objects.includes(item.code)}
              title={item.title}
              onClick={() => setObjectCode(item.code)}
            >
              {item.label}
            </Chip>
          ))}
        </div>
        {!area && <p className={styles.note}>Сначала выберите область аттестации.</p>}
      </div>

      <div className={styles.group}>
        <span className={styles.label}>Категория</span>
        <div className={styles.chips} role="group" aria-label="Категория">
          {catalog.categories.map((item) => (
            <Chip key={item} active={category === item} onClick={() => setCategory(item)}>
              {item} категория
            </Chip>
          ))}
        </div>
      </div>

      <div className={styles.fields}>
        <TextField
          label="Дата окончания срока действия квалификационного удостоверения"
          type="date"
          value={validUntil}
          onChange={setValidUntil}
        />
        <TextField
          label="Номер квалификационного удостоверения либо номер регистрации в ЕРУЛ"
          maxLength={64}
          value={number}
          onChange={setNumber}
        />
      </div>

      {error && <p className={styles.error}>{error}</p>}

      <div className={styles.actions}>
        <OutlineButton disabled={pending} onClick={onCancel}>
          Отмена
        </OutlineButton>
        <Button disabled={!complete} loading={pending} onClick={submit}>
          {initial ? "Сохранить" : "Добавить"}
        </Button>
      </div>
    </div>
  );
};

export default CertificateForm;
