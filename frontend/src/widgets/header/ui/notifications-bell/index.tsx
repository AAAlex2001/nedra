"use client";

import { useEffect, useRef, useState } from "react";
import { formatRequestDate } from "@/entities/request";
import { useNotifications } from "@/features/notifications";
import { BellIcon } from "@/shared/ui/icons";
import styles from "./style.module.scss";

const NotificationsBell = () => {
  const { state, markRead } = useNotifications();
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);

  const items = state.status === "ready" ? state.items : [];
  const unread = items.filter((item) => item.read_at === null).length;

  useEffect(() => {
    if (!open) return;

    const closeOnClickOutside = (event: MouseEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false);
    };
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };

    document.addEventListener("mousedown", closeOnClickOutside);
    document.addEventListener("keydown", closeOnEscape);

    return () => {
      document.removeEventListener("mousedown", closeOnClickOutside);
      document.removeEventListener("keydown", closeOnEscape);
    };
  }, [open]);

  return (
    <div className={styles.root} ref={rootRef}>
      <button
        type="button"
        className={styles.button}
        aria-label={unread > 0 ? `Уведомления, непрочитанных: ${unread}` : "Уведомления"}
        aria-expanded={open}
        onClick={() => setOpen(!open)}
      >
        <BellIcon className={styles.icon} />
        {unread > 0 && <span className={styles.badge}>{unread > 9 ? "9+" : unread}</span>}
      </button>

      {open && (
        <div className={styles.popup}>
          <span className={styles.popupTitle}>Уведомления</span>

          {items.length === 0 ? (
            <p className={styles.empty}>Уведомлений пока нет.</p>
          ) : (
            <ul className={styles.list}>
              {items.slice(0, 8).map((item) => (
                <li
                  key={item.id}
                  className={`${styles.item} ${item.read_at === null ? styles.itemUnread : ""}`}
                >
                  <p className={styles.text}>{item.text}</p>
                  <div className={styles.itemFoot}>
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
          )}
        </div>
      )}
    </div>
  );
};

export default NotificationsBell;
