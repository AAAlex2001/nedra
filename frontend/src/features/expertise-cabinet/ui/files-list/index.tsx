import { expertiseDocumentUrl, type ExpertiseDocument } from "@/entities/expertise";
import { DocumentIcon } from "@/shared/ui/icons";
import styles from "./style.module.scss";

type FilesListProps = {
  expertiseId: number;
  documents: ExpertiseDocument[];
};

const FilesList = ({ expertiseId, documents }: FilesListProps) => (
  <ul className={styles.files}>
    {documents.map((document) => (
      <li key={document.id}>
        <a
          className={styles.file}
          href={expertiseDocumentUrl(expertiseId, document.id)}
          target="_blank"
          rel="noreferrer"
          title={document.original_name}
        >
          <span className={styles.tile}>
            <DocumentIcon className={styles.icon} />
          </span>
          {document.item_number !== null && (
            <span className={styles.item}>п. {document.item_number}</span>
          )}
          <span className={styles.name}>{document.original_name}</span>
        </a>
      </li>
    ))}
  </ul>
);

export default FilesList;
