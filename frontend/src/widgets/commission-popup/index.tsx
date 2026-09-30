"use client";

import Image from "next/image";
import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { fetchExpertCatalog, type ExpertCatalog } from "@/entities/expert";
import { CommissionApplicationForm } from "@/features/commission-application";
import Button from "@/shared/ui/button";
import { CheckIcon, CloseIcon } from "@/shared/ui/icons";
import styles from "./style.module.scss";

const SHOW_DELAY = 4000;
const STORAGE_KEY = "nedra-commission-popup";
const CATALOG_FAILED = "Не удалось загрузить справочник областей аттестации. Попробуйте позже.";

const OBJECTS = [
  "проекты консервации и ликвидации",
  "проекты технического перевооружения",
  "декларации промышленной безопасности",
  "обоснования безопасности",
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

  const openForm = async () => {
    setStep("form");
    if (catalog) return;

    try {
      const loaded = await fetchExpertCatalog();
      setCatalog(loaded);
    } catch {
      setCatalogError(CATALOG_FAILED);
    }
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
        <div className={styles.head}>
          <span className={styles.badge}>Конкурсный отбор</span>
          <button type="button" className={styles.close} aria-label="Закрыть" onClick={close}>
            <CloseIcon className={styles.closeIcon} />
          </button>
        </div>

        {step === "intro" ? (
          <div className={styles.intro}>
            <div className={styles.lead}>
              <Image
                className={styles.image}
                src="/blitz/10.webp"
                alt=""
                width={400}
                height={400}
                sizes="120px"
              />
              <div className={styles.leadText}>
                <p className={styles.title}>Примем эксперта</p>
                <p className={styles.text}>
                  для выполнения работ по экспертизе промышленной безопасности объектов:
                </p>
              </div>
            </div>

            <ul className={styles.objects}>
              {OBJECTS.map((item) => (
                <li key={item} className={styles.object}>
                  <CheckIcon className={styles.objectIcon} />
                  <span className={styles.objectText}>{item}</span>
                </li>
              ))}
            </ul>

            <Button className={styles.cta} onClick={() => void openForm()}>
              Оставить заявку в конкурсную комиссию
            </Button>
          </div>
        ) : (
          <div className={styles.formStep}>
            <button type="button" className={styles.back} onClick={() => setStep("intro")}>
              ← Назад
            </button>
            <p className={styles.formTitle}>Заявка в конкурсную комиссию</p>

            {catalog && <CommissionApplicationForm catalog={catalog} onClose={close} />}
            {!catalog && !catalogError && <p className={styles.text}>Загружаем справочник…</p>}
            {catalogError && <p className={styles.error}>{catalogError}</p>}
          </div>
        )}
      </div>
    </div>,
    document.body,
  );
};

export default CommissionPopup;
