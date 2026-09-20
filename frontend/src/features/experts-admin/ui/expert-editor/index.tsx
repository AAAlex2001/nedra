"use client";

import { useState } from "react";
import type { Certificate, ExpertCatalog } from "@/entities/expert";
import Button from "@/shared/ui/button";
import Chip from "@/shared/ui/chip";
import SelectField from "@/shared/ui/select-field";
import TextField from "@/shared/ui/text-field";
import { deleteCertificate, updateCertificate, updateExpert } from "../../api/experts";
import styles from "./style.module.scss";

type ExpertEditorProps = {
  userId: number;
  fullName: string;
  phone: string;
  directions: string[];
  certificates: Certificate[];
  catalog: ExpertCatalog | null;
  basePath: string;
  onUpdated: () => void;
};

type CertificateRowProps = {
  userId: number;
  certificate: Certificate;
  catalog: ExpertCatalog | null;
  basePath: string;
  onUpdated: () => void;
};

const describe = (error: unknown, fallback: string): string =>
  error instanceof Error && error.message ? error.message : fallback;

const CertificateRow = ({
  userId,
  certificate,
  catalog,
  basePath,
  onUpdated,
}: CertificateRowProps) => {
  const [areaCode, setAreaCode] = useState(certificate.area_code);
  const [objectCode, setObjectCode] = useState(certificate.object_code);
  const [category, setCategory] = useState(String(certificate.category));
  const [validUntil, setValidUntil] = useState(certificate.valid_until);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const areas = catalog ? catalog.areas : [];
  const selectedArea = areas.find((item) => item.code === areaCode);
  const objects = catalog ? catalog.objects : [];
  const allowed = objects.filter((item) => selectedArea?.objects.includes(item.code));

  const selectArea = (code: string) => {
    setAreaCode(code);

    const area = areas.find((item) => item.code === code);
    if (area && !area.objects.includes(objectCode)) setObjectCode(area.objects[0] ?? "");
  };

  const save = async () => {
    setPending(true);
    setError(null);

    try {
      await updateCertificate(basePath, userId, certificate.id, {
        area_code: areaCode,
        object_code: objectCode,
        category: Number(category),
        valid_until: validUntil,
      });
      onUpdated();
    } catch (caught) {
      setError(describe(caught, "Не удалось сохранить удостоверение"));
    } finally {
      setPending(false);
    }
  };

  const remove = async () => {
    if (!window.confirm("Удалить это удостоверение?")) return;

    setPending(true);
    setError(null);

    try {
      await deleteCertificate(basePath, userId, certificate.id);
      onUpdated();
    } catch (caught) {
      setError(describe(caught, "Не удалось удалить удостоверение"));
    } finally {
      setPending(false);
    }
  };

  return (
    <div className={styles.certificate}>
      <div className={styles.fields}>
        <SelectField
          label="Область"
          placeholder="Выберите область"
          value={areaCode}
          onChange={selectArea}
          options={areas.map((area) => ({ value: area.code, label: area.code, hint: area.title }))}
        />
        <SelectField
          label="Объект"
          placeholder="Выберите объект"
          value={objectCode}
          onChange={setObjectCode}
          options={allowed.map((item) => ({
            value: item.code,
            label: item.label,
            hint: item.title,
          }))}
        />
        <SelectField
          label="Категория"
          placeholder="Категория"
          value={category}
          onChange={setCategory}
          options={[
            { value: "1", label: "1" },
            { value: "2", label: "2" },
            { value: "3", label: "3" },
          ]}
        />
        <TextField label="Действует до" type="date" value={validUntil} onChange={setValidUntil} />
      </div>

      <div className={styles.rowButtons}>
        <button type="button" className={styles.remove} disabled={pending} onClick={remove}>
          Удалить
        </button>
        <Button loading={pending} onClick={() => void save()}>
          Сохранить
        </Button>
      </div>

      {error && <p className={styles.error}>{error}</p>}
    </div>
  );
};

const ExpertEditor = ({
  userId,
  fullName,
  phone,
  directions,
  certificates,
  catalog,
  basePath,
  onUpdated,
}: ExpertEditorProps) => {
  const [name, setName] = useState(fullName);
  const [contact, setContact] = useState(phone);
  const [chosen, setChosen] = useState(directions);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const toggleDirection = (code: string) => {
    if (chosen.includes(code)) {
      setChosen(chosen.filter((item) => item !== code));
      return;
    }

    setChosen([...chosen, code]);
  };

  const save = async () => {
    setPending(true);
    setError(null);

    try {
      await updateExpert(basePath, userId, {
        full_name: name.trim(),
        phone: contact.trim(),
        directions: chosen,
      });
      onUpdated();
    } catch (caught) {
      setError(describe(caught, "Не удалось сохранить данные эксперта"));
    } finally {
      setPending(false);
    }
  };

  return (
    <div className={styles.editor}>
      <div className={styles.fields}>
        <TextField label="ФИО" value={name} onChange={setName} />
        <TextField label="Телефон" type="tel" value={contact} onChange={setContact} />
      </div>

      <div className={styles.group}>
        <span className={styles.label}>Направления работы</span>
        <div className={styles.chips}>
          {(catalog ? catalog.directions : []).map((direction) => (
            <Chip
              key={direction.code}
              active={chosen.includes(direction.code)}
              onClick={() => toggleDirection(direction.code)}
            >
              {direction.title}
            </Chip>
          ))}
        </div>
      </div>

      <Button loading={pending} onClick={() => void save()}>
        Сохранить данные
      </Button>

      {error && <p className={styles.error}>{error}</p>}

      <div className={styles.group}>
        <span className={styles.label}>Удостоверения</span>
        {certificates.map((certificate) => (
          <CertificateRow
            key={certificate.id}
            userId={userId}
            certificate={certificate}
            catalog={catalog}
            basePath={basePath}
            onUpdated={onUpdated}
          />
        ))}
      </div>
    </div>
  );
};

export default ExpertEditor;
