import type { ExpertiseDocument, ExpertiseRemark } from "@/entities/expertise";
import { formatRequestDate } from "@/entities/request";
import FilesList from "../files-list";
import styles from "./style.module.scss";

type RemarksThreadProps = {
  expertiseId: number;
  remarks: ExpertiseRemark[];
};

type MessageProps = {
  expertiseId: number;
  author: "Эксперт" | "Заказчик";
  date: string;
  text: string | null;
  documents: ExpertiseDocument[];
};

const Message = ({ expertiseId, author, date, text, documents }: MessageProps) => {
  const tone = author === "Эксперт" ? styles.fromExpert : styles.fromCustomer;
  const fallback = documents.length === 0 ? "Исправленная документация отправлена повторно" : null;

  return (
    <div className={styles.message}>
      <span className={`${styles.avatar} ${tone}`} aria-hidden="true">
        {author[0]}
      </span>

      <div className={styles.body}>
        <p className={styles.meta}>
          <span className={styles.author}>{author}</span> · {formatRequestDate(date)}
        </p>
        {(text ?? fallback) && <p className={styles.text}>{text ?? fallback}</p>}
        {documents.length > 0 && <FilesList expertiseId={expertiseId} documents={documents} />}
      </div>
    </div>
  );
};

const RemarksThread = ({ expertiseId, remarks }: RemarksThreadProps) => {
  const last = remarks[remarks.length - 1];
  const resolved = last !== undefined && last.resolved_at !== null;

  return (
    <section className={styles.root}>
      <header className={styles.head}>
        <h4 className={styles.title}>
          Рекомендации по приведению объекта экспертизы в соответствие с требованиями промышленной
          безопасности
        </h4>
        <span className={resolved ? styles.done : styles.wait}>
          {resolved ? "Исправления отправлены" : "Ждём исправления"}
        </span>
      </header>

      <ol className={styles.thread}>
        {remarks.map((remark) => (
          <li key={remark.id} className={styles.round}>
            <Message
              expertiseId={expertiseId}
              author="Эксперт"
              date={remark.created_at}
              text={remark.text}
              documents={remark.documents.filter((item) => item.kind === "remarks")}
            />
            {remark.resolved_at && (
              <Message
                expertiseId={expertiseId}
                author="Заказчик"
                date={remark.resolved_at}
                text={remark.response_text}
                documents={remark.documents.filter((item) => item.kind === "revision")}
              />
            )}
          </li>
        ))}
      </ol>
    </section>
  );
};

export default RemarksThread;
