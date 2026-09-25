"use client";

import { useState } from "react";
import {
  directionTitle,
  type CertificateInput,
  type ExpertCatalog,
  type ExpertProfile,
} from "@/entities/expert";
import { formatDate } from "@/shared/lib/date";
import { DetailsRow, DetailsTable } from "@/shared/ui/details-table";
import Button from "@/shared/ui/button";
import { useCertificates } from "../../model/use-certificates";
import CertificateCard from "../certificate-card";
import CertificateForm from "../certificate-form";
import styles from "./style.module.scss";

type ExpertAttestationProps = {
  profile: ExpertProfile;
  catalog: ExpertCatalog;
  onChange: (profile: ExpertProfile) => void;
};

type Editing = number | "new" | null;

const ExpertAttestation = ({ profile, catalog, onChange }: ExpertAttestationProps) => {
  const [editing, setEditing] = useState<Editing>(null);
  const actions = useCertificates(onChange);

  const directions = profile.directions.map((code) => directionTitle(catalog, code));
  const certificates = profile.certificates;
  const removable = certificates.length > 1;

  const open = (target: Editing) => {
    actions.clearError();
    setEditing(target);
  };

  const submit = async (input: CertificateInput) => {
    const saved =
      editing === "new"
        ? await actions.add(input)
        : await actions.update(Number(editing), input);

    if (saved) setEditing(null);
  };

  const remove = (id: number) => {
    actions.clearError();
    void actions.remove(id);
  };

  return (
    <div className={styles.attestation}>
      <DetailsTable>
        <DetailsRow label="Направления работы">{directions.join(", ")}</DetailsRow>
        <DetailsRow label="Эксперт платформы">с {formatDate(profile.approved_at)}</DetailsRow>
      </DetailsTable>

      <section className={styles.section}>
        <div className={styles.head}>
          <h3 className={styles.title}>
            Удостоверения <span className={styles.count}>{certificates.length}</span>
          </h3>
          <p className={styles.hint}>
            Заявки приходят по областям и объектам из ваших удостоверений. Если какое-то забыли
            указать при регистрации — добавьте его здесь.
          </p>
        </div>

        <div className={styles.list}>
          {certificates.map((certificate) =>
            editing === certificate.id ? (
              <CertificateForm
                key={certificate.id}
                catalog={catalog}
                initial={certificate}
                pending={actions.pending}
                error={actions.error}
                onSubmit={(input) => void submit(input)}
                onCancel={() => setEditing(null)}
              />
            ) : (
              <CertificateCard
                key={certificate.id}
                certificate={certificate}
                catalog={catalog}
                pending={actions.pending}
                removable={removable}
                onEdit={() => open(certificate.id)}
                onRemove={() => remove(certificate.id)}
              />
            ),
          )}

          {editing === "new" ? (
            <CertificateForm
              catalog={catalog}
              initial={null}
              pending={actions.pending}
              error={actions.error}
              onSubmit={(input) => void submit(input)}
              onCancel={() => setEditing(null)}
            />
          ) : (
            <Button className={styles.add} onClick={() => open("new")}>
              Добавить удостоверение
            </Button>
          )}
        </div>

        {editing === null && actions.error && <p className={styles.error}>{actions.error}</p>}
      </section>
    </div>
  );
};

export default ExpertAttestation;
