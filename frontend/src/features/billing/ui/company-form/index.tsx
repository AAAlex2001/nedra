"use client";

import { useState } from "react";
import type { Company } from "@/entities/billing";
import Button from "@/shared/ui/button";
import Loader from "@/shared/ui/loader";
import TextField from "@/shared/ui/text-field";
import { useCompany } from "../../model/use-company";
import styles from "./style.module.scss";

type FieldsProps = {
  company: Company | null;
  pending: boolean;
  error: string | null;
  onSave: (draft: { name: string; inn: string; kpp: string | null; address: string }) => void;
};

const CompanyFields = ({ company, pending, error, onSave }: FieldsProps) => {
  const [name, setName] = useState(company?.name ?? "");
  const [inn, setInn] = useState(company?.inn ?? "");
  const [kpp, setKpp] = useState(company?.kpp ?? "");
  const [address, setAddress] = useState(company?.address ?? "");

  const canSubmit = name.trim() !== "" && inn.trim() !== "" && address.trim() !== "" && !pending;

  const save = () => {
    if (!canSubmit) return;

    onSave({
      name: name.trim(),
      inn: inn.trim(),
      kpp: kpp.trim() === "" ? null : kpp.trim(),
      address: address.trim(),
    });
  };

  return (
    <div className={styles.form}>
      <p className={styles.hint}>
        Эти реквизиты попадут в счёт на оплату и в акт выполненных работ.
      </p>

      <TextField
        label="Название организации"
        required
        placeholder="ООО «Ромашка»"
        value={name}
        onChange={setName}
      />

      <div className={styles.row}>
        <TextField
          label="ИНН"
          required
          inputMode="numeric"
          placeholder="7701234567"
          maxLength={12}
          value={inn}
          onChange={setInn}
        />
        <TextField
          label="КПП"
          inputMode="numeric"
          placeholder="770101001"
          maxLength={9}
          value={kpp}
          onChange={setKpp}
        />
      </div>

      <TextField
        label="Юридический адрес"
        required
        placeholder="630008, Новосибирск, ул. Кирова, 113/2"
        value={address}
        onChange={setAddress}
      />

      {error && <p className={styles.error}>{error}</p>}

      <Button className={styles.submit} disabled={!canSubmit} loading={pending} onClick={save}>
        Сохранить реквизиты
      </Button>
    </div>
  );
};

const CompanyForm = () => {
  const { state, pending, saveError, save } = useCompany();

  if (state.status === "loading") {
    return <Loader />;
  }

  if (state.status === "error") {
    return <p className={styles.error}>{state.message}</p>;
  }

  return (
    <CompanyFields
      key={state.company?.updated_at ?? "new"}
      company={state.company}
      pending={pending}
      error={saveError}
      onSave={(draft) => void save(draft)}
    />
  );
};

export default CompanyForm;
