"use client";

import { useState } from "react";
import type { ExpertCatalog } from "@/entities/expert";
import Button from "@/shared/ui/button";
import Checkbox from "@/shared/ui/checkbox";
import Chip from "@/shared/ui/chip";
import TextField from "@/shared/ui/text-field";
import { useAdminAction } from "../../model/use-admin-action";
import { updateExpert } from "../../api/experts";
import styles from "./style.module.scss";

type ExpertContactsProps = {
  userId: number;
  fullName: string;
  phone: string;
  directions: string[];
  auditLead: boolean;
  catalog: ExpertCatalog | null;
  basePath: string;
  onUpdated: () => void;
};

const AUDIT_DIRECTION = "sms_audit";

const ExpertContacts = ({
  userId,
  fullName,
  phone,
  directions,
  auditLead,
  catalog,
  basePath,
  onUpdated,
}: ExpertContactsProps) => {
  const [name, setName] = useState(fullName);
  const [contact, setContact] = useState(phone);
  const [chosen, setChosen] = useState(directions);
  const [lead, setLead] = useState(auditLead);
  const { pending, error, run } = useAdminAction();
  const auditor = chosen.includes(AUDIT_DIRECTION);

  const toggleDirection = (code: string) => {
    if (chosen.includes(code)) {
      setChosen(chosen.filter((item) => item !== code));
      return;
    }

    setChosen([...chosen, code]);
  };

  const save = () =>
    run(async () => {
      await updateExpert(basePath, userId, {
        full_name: name.trim(),
        phone: contact.trim(),
        directions: chosen,
        audit_lead: auditor && lead,
      });
      onUpdated();
    });

  return (
    <section className={styles.block}>
      <h3 className={styles.title}>Данные эксперта</h3>

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

      {auditor && (
        <Checkbox checked={lead} onChange={setLead}>
          Может быть руководителем аудиторской группы: берёт заявки на аудит и формирует группу
        </Checkbox>
      )}

      {error && <p className={styles.error}>{error}</p>}

      <div className={styles.actions}>
        <Button loading={pending} onClick={() => void save()}>
          Сохранить
        </Button>
      </div>
    </section>
  );
};

export default ExpertContacts;
