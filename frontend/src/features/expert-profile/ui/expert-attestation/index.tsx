import { Fragment } from "react";
import {
  areaTitle,
  directionTitle,
  myCertificateScanUrl,
  objectLabel,
  objectTitle,
  type ExpertCatalog,
  type ExpertProfile,
} from "@/entities/expert";
import { formatDate } from "@/shared/lib/date";
import { DetailsRow, DetailsTable } from "@/shared/ui/details-table";
import { DocumentIcon } from "@/shared/ui/icons";
import styles from "./style.module.scss";

type ExpertAttestationProps = {
  profile: ExpertProfile;
  catalog: ExpertCatalog;
};

const ExpertAttestation = ({ profile, catalog }: ExpertAttestationProps) => {
  const directions = profile.directions.map((code) => directionTitle(catalog, code));

  return (
    <DetailsTable>
      <DetailsRow label="Направления работы">{directions.join(", ")}</DetailsRow>
      <DetailsRow label="Эксперт платформы">с {formatDate(profile.approved_at)}</DetailsRow>

      {profile.certificates.length === 0 && (
        <DetailsRow label="Удостоверения">
          <span className={styles.muted}>Удостоверений пока нет</span>
        </DetailsRow>
      )}

      {profile.certificates.map((item) => (
        <Fragment key={item.id}>
          <DetailsRow label="Область аттестации">
            <span className={styles.code}>{item.area_code}</span>
            {areaTitle(catalog, item.area_code)}
          </DetailsRow>
          <DetailsRow label="Вид экспертизы">
            <span className={styles.code}>{objectLabel(catalog, item.object_code)}</span>
            {objectTitle(catalog, item.object_code)}
          </DetailsRow>
          <DetailsRow label="Категория">{item.category}</DetailsRow>
          <DetailsRow label="Действует до">{formatDate(item.valid_until)}</DetailsRow>
          {item.number && (
            <DetailsRow label="Номер удостоверения или ЕРУЛ">{item.number}</DetailsRow>
          )}
          {item.scan_name && (
            <DetailsRow label="Скан удостоверения">
              <a
                className={styles.scan}
                href={myCertificateScanUrl(item.id)}
                target="_blank"
                rel="noreferrer"
                title={item.scan_name}
              >
                <span className={styles.scanTile}>
                  <DocumentIcon className={styles.scanIcon} />
                </span>
                <span className={styles.scanName}>{item.scan_name}</span>
              </a>
            </DetailsRow>
          )}
        </Fragment>
      ))}
    </DetailsTable>
  );
};

export default ExpertAttestation;
