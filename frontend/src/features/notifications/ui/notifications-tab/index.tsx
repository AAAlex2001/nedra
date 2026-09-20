"use client";

import { formatRequestDate } from "@/entities/request";
import Loader from "@/shared/ui/loader";
import type { useNotifications } from "../../model/use-notifications";
import styles from "./style.module.scss";

type NotificationsTabProps = {
  notifications: ReturnType<typeof useNotifications>;
};

const NotificationsTab = ({ notifications }: NotificationsTabProps) => {
  const { state, items, unread, pending, markRead, markAllRead } = notifications;

  if (state.status === "loading") {
    return <Loader />;
  }

  if (state.status === "error") {
    return <p className={styles.error}>{state.message}</p>;
  }

  if (items.length === 0) {
    return (
      <div className={styles.empty}>
        <p className={styles.emptyTitle}>Уведомлений пока нет</p>
        <p className={styles.emptyText}>
          Здесь появятся сообщения о каждом шаге по вашим заявкам: новые заявки, замечания,
          оплата, заключение.
        </p>
      </div>
    );
  }

  return (
    <div className={styles.root}>
      <div className={styles.toolbar}>
        <span className={styles.count}>
          {unread > 0 ? `Непрочитанных: ${unread}` : "Всё прочитано"}
        </span>
        {unread > 0 && (
          <button
            type="button"
            className={styles.readAll}
            disabled={pending}
            onClick={() => void markAllRead()}
          >
            Прочитать все
          </button>
        )}
      </div>

      <ul className={styles.list}>
        {items.map((item) => (
          <li
            key={item.id}
            className={`${styles.item} ${item.read_at === null ? styles.itemUnread : ""}`}
          >
            <p className={styles.text}>{item.text}</p>
            <div className={styles.foot}>
              <time className={styles.date} dateTime={item.created_at}>
                {formatRequestDate(item.created_at)}
              </time>
              {item.read_at === null && (
                <button
                  type="button"
                  className={styles.read}
                  onClick={() => void markRead(item.id)}
                >
                  Прочитано
                </button>
              )}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default NotificationsTab;
