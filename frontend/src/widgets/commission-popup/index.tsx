"use client";

import Image from "next/image";
import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { fetchExpertCatalog, type ExpertCatalog } from "@/entities/expert";
import { CommissionApplicationForm } from "@/features/commission-application";
import Button from "@/shared/ui/button";
import { CheckIcon, ChevronIcon, CloseIcon } from "@/shared/ui/icons";
import Spinner from "@/shared/ui/spinner";
import styles from "./style.module.scss";

const SHOW_DELAY = 4000;
const STORAGE_KEY = "nedra-commission-popup";
const CATALOG_FAILED = "Не удалось загрузить справочник областей аттестации. Попробуйте позже.";

const OBJECTS = [
  "Проекты консервации и ликвидации",
  "Проекты технического перевооружения",
  "Декларации промышленной безопасности",
  "Обоснования безопасности",
];

type Step = "intro" | "form";

const wasClosed = (): boolean => {
  try {
    return window.localStorage.getItem(STORAGE_KEY) === "closed";
  } catch {
    return false;
  }
};

const rememberClosed = () => {
  try {
    window.localStorage.setItem(STORAGE_KEY, "closed");
  } catch {
    return;
  }
};

const CommissionPopup = () => {
  const [open, setOpen] = useState(false);
  const [step, setStep] = useState<Step>("intro");
  const [catalog, setCatalog] = useState<ExpertCatalog | null>(null);
  const [catalogError, setCatalogError] = useState<string | null>(null);

  useEffect(() => {
    if (wasClosed()) return;

    const timer = window.setTimeout(() => setOpen(true), SHOW_DELAY);

    return () => window.clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (!open) return;

    const loadCatalog = async () => {
      try {
        const loaded = await fetchExpertCatalog();
        setCatalog(loaded);
      } catch {
        setCatalogError(CATALOG_FAILED);
      }
    };

    void loadCatalog();
  }, [open]);

  useEffect(() => {
    if (!open) return;

    const onKey = (event: KeyboardEvent) => {
      if (event.key !== "Escape") return;
      rememberClosed();
      setOpen(false);
    };

    document.addEventListener("keydown", onKey);
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = previousOverflow;
    };
  }, [open]);

  const close = () => {
    rememberClosed();
    setOpen(false);
  };

  if (!open) return null;

  return createPortal(
    <div className={styles.overlay} onClick={close}>
      <div
        className={styles.window}
        role="dialog"
        aria-modal="true"
        aria-label="Конкурсный отбор экспертов"
        onClick={(event) => event.stopPropagation()}
      >
        {step === "intro" ? (
          <>
            <div className={styles.media}>
              <Image
                className={styles.image}
                src="/blitz/23.webp"
                alt="Документация, заключение экспертизы и оборудование опасного производственного объекта"
                width={1600}
                height={700}
                sizes="(min-width: 768px) 640px, 100vw"
                priority
              />
              <button
                type="button"
                className={`${styles.round} ${styles.closeOnImage}`}
                aria-label="Закрыть"
                onClick={close}
              >
                <CloseIcon className={styles.roundIcon} />
              </button>
            </div>

            <div className={styles.content}>
              <span className={styles.badge}>Конкурсный отбор</span>

              <p className={styles.title}>Примем эксперта</p>
              <p className={styles.lead}>
                для выполнения работ по экспертизе промышленной безопасности следующих объектов:
              </p>

              <ul className={styles.points}>
                {OBJECTS.map((item) => (
                  <li key={item} className={styles.point}>
                    <CheckIcon className={styles.pointIcon} />
                    <span className={styles.pointText}>{item}</span>
                  </li>
                ))}
              </ul>

              <Button className={styles.cta} onClick={() => setStep("form")}>
                Оставить заявку в конкурсную комиссию
              </Button>
            </div>
          </>
        ) : (
          <div className={`${styles.content} ${styles.formContent}`}>
            <div className={styles.formHead}>
              <button
                type="button"
                className={styles.round}
                aria-label="Назад"
                onClick={() => setStep("intro")}
              >
                <ChevronIcon className={`${styles.roundIcon} ${styles.backIcon}`} />
              </button>
              <p className={styles.formTitle}>Заявка в конкурсную комиссию</p>
              <button type="button" className={styles.round} aria-label="Закрыть" onClick={close}>
                <CloseIcon className={styles.roundIcon} />
              </button>
            </div>

            {catalog && <CommissionApplicationForm catalog={catalog} onClose={close} />}
            {!catalog && !catalogError && (
              <div className={styles.loader}>
                <Spinner size={32} />
              </div>
            )}
            {catalogError && <p className={styles.error}>{catalogError}</p>}
          </div>
        )}
      </div>
    </div>,
    document.body,
  );
};

export default CommissionPopup;
