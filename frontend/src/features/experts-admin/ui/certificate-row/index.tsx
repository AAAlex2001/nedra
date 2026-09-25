"use client";

import { useState } from "react";
import {
  areaTitle,
  objectTitle,
  type Certificate,
  type ExpertCatalog,
} from "@/entities/expert";
import Button from "@/shared/ui/button";
import OutlineButton from "@/shared/ui/outline-button";
import SelectField from "@/shared/ui/select-field";
import TextField from "@/shared/ui/text-field";
import { useAdminAction } from "../../model/use-admin-action";
import { createCertificate, deleteCertificate, updateCertificate } from "../../api/experts";
import styles from "./style.module.scss";

type CertificateRowProps = {
  userId: number;
  certificate: Certificate | null;
  catalog: ExpertCatalog | null;
  basePath: string;
  onUpdated: () => void;
  onCancel?: () => void;
};

const CATEGORIES = [
  { value: "1", label: "1" },
  { value: "2", label: "2" },
  { value: "3", label: "3" },
];

const CertificateRow = ({
  userId,
  certificate,
  catalog,
  basePath,
  onUpdated,
  onCancel,
}: CertificateRowProps) => {
  const [areaCode, setAreaCode] = useState(certificate?.area_code ?? "");
  const [objectCode, setObjectCode] = useState(certificate?.object_code ?? "");
  const [category, setCategory] = useState(certificate ? String(certificate.category) : "");
  const [validUntil, setValidUntil] = useState(certificate?.valid_until ?? "");
  const [number, setNumber] = useState(certificate?.number ?? "");
  const { pending, error, run } = useAdminAction();

  const areas = catalog ? catalog.areas : [];
  const objects = catalog ? catalog.objects : [];
  const selectedArea = areas.find((item) => item.code === areaCode);
  const allowed = objects.filter((item) => selectedArea?.objects.includes(item.code));

  const selectArea = (code: string) => {
    setAreaCode(code);

    const area = areas.find((item) => item.code === code);
    if (area && !area.objects.includes(objectCode)) setObjectCode(area.objects[0] ?? "");
  };

  const save = () =>
    run(async () => {
      const payload = {
        area_code: areaCode,
        object_code: objectCode,
        category: Number(category),
        valid_until: validUntil,
        number: number.trim(),
      };

      if (certificate) {
        await updateCertificate(basePath, userId, certificate.id, payload);
      } else {
        await createCertificate(basePath, userId, payload);
        onCancel?.();
      }

      onUpdated();
    });

  const remove = () => {
    if (!certificate || !window.confirm("Удалить это удостоверение?")) return;

    void run(async () => {
      await deleteCertificate(basePath, userId, certificate.id);
      onUpdated();
    });
  };

  return (
    <article className={styles.row}>
      <div className={styles.fields}>
        <SelectField
          label="Область"
          placeholder="Выберите"
          value={areaCode}
          onChange={selectArea}
          options={areas.map((area) => ({ value: area.code, label: area.code }))}
        />
        <SelectField
          label="Объект"
          placeholder="Выберите"
          value={objectCode}
          onChange={setObjectCode}
          options={allowed.map((item) => ({ value: item.code, label: item.label }))}
        />
        <SelectField
          label="Категория"
          placeholder="Категория"
          value={category}
          onChange={setCategory}
          options={CATEGORIES}
        />
        <TextField label="Действует до" type="date" value={validUntil} onChange={setValidUntil} />
        <TextField label="Номер или ЕРУЛ" maxLength={64} value={number} onChange={setNumber} />
      </div>

      {catalog && areaCode && objectCode && (
        <p className={styles.caption}>
          {areaTitle(catalog, areaCode)} · {objectTitle(catalog, objectCode)}
        </p>
      )}

      {error && <p className={styles.error}>{error}</p>}

      <div className={styles.actions}>
        {certificate ? (
          <button type="button" className={styles.remove} disabled={pending} onClick={remove}>
            Удалить
          </button>
        ) : (
          <OutlineButton disabled={pending} onClick={onCancel}>
            Отмена
          </OutlineButton>
        )}
        <Button loading={pending} onClick={() => void save()}>
          {certificate ? "Сохранить" : "Добавить"}
        </Button>
      </div>
    </article>
  );
};

export default CertificateRow;
