"use client";

import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { fetchExpertCatalog, type ExpertCatalog } from "@/entities/expert";
import {
  CommissionApplicationForm,
  CommissionOffer,
  useCommissionPopup,
  wasPopupClosed,
} from "@/features/commission-application";
import { ChevronIcon, CloseIcon } from "@/shared/ui/icons";
import Spinner from "@/shared/ui/spinner";
import styles from "./style.module.scss";

const SHOW_DELAY = 4000;
const CATALOG_FAILED = "Не удалось загрузить справочник областей аттестации. Попробуйте позже.";

const CommissionPopup = () => {
  const { open, step, openIntro, showStep, close } = useCommissionPopup();
  const [catalog, setCatalog] = useState<ExpertCatalog | null>(null);
  const [catalogError, setCatalogError] = useState<string | null>(null);

  useEffect(() => {
    if (wasPopupClosed()) return;

    const timer = window.setTimeout(openIntro, SHOW_DELAY);

    return () => window.clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (!open || catalog) return;

    const loadCatalog = async () => {
      try {
        const loaded = await fetchExpertCatalog();
        setCatalog(loaded);
      } catch {
        setCatalogError(CATALOG_FAILED);
      }
    };

    void loadCatalog();
  }, [open, catalog]);

  useEffect(() => {
    if (!open) return;

    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") close();
    };

    document.addEventListener("keydown", onKey);
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = previousOverflow;
    };
  }, [open, close]);

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
          <CommissionOffer onApply={() => showStep("form")} onClose={close} />
        ) : (
          <div className={styles.frame}>
            <div className={styles.content}>
              <div className={styles.head}>
                <button
                  type="button"
                  className={styles.round}
                  aria-label="Назад"
                  onClick={() => showStep("intro")}
                >
                  <ChevronIcon className={`${styles.roundIcon} ${styles.backIcon}`} />
                </button>
                <p className={styles.title}>Заявка в конкурсную комиссию</p>
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
          </div>
        )}
      </div>
    </div>,
    document.body,
  );
};

export default CommissionPopup;
