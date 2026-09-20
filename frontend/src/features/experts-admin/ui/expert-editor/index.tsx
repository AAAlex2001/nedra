import type { Certificate, ExpertCatalog } from "@/entities/expert";
import CertificateRow from "../certificate-row";
import ExpertContacts from "../expert-contacts";
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

const ExpertEditor = ({
  userId,
  fullName,
  phone,
  directions,
  certificates,
  catalog,
  basePath,
  onUpdated,
}: ExpertEditorProps) => (
  <div className={styles.editor}>
    <ExpertContacts
      userId={userId}
      fullName={fullName}
      phone={phone}
      directions={directions}
      catalog={catalog}
      basePath={basePath}
      onUpdated={onUpdated}
    />

    <section className={styles.block}>
      <h3 className={styles.title}>Удостоверения</h3>

      {certificates.length === 0 ? (
        <p className={styles.empty}>Удостоверений нет.</p>
      ) : (
        certificates.map((certificate) => (
          <CertificateRow
            key={certificate.id}
            userId={userId}
            certificate={certificate}
            catalog={catalog}
            basePath={basePath}
            onUpdated={onUpdated}
          />
        ))
      )}
    </section>
  </div>
);

export default ExpertEditor;
