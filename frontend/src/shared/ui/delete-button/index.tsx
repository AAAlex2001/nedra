"use client";

import { useRef, useState, type ReactNode } from "react";
import Button from "@/shared/ui/button";
import Modal from "@/shared/ui/modal";
import OutlineButton from "@/shared/ui/outline-button";
import styles from "./style.module.scss";

type DeleteButtonProps = {
  title: string;
  description: string;
  onConfirm: () => void | Promise<void>;
  children?: ReactNode;
  className?: string;
  disabled?: boolean;
  "aria-label"?: string;
};

const DeleteButton = ({
  title,
  description,
  onConfirm,
  children = "Удалить",
  className,
  disabled,
  "aria-label": ariaLabel,
}: DeleteButtonProps) => {
  const [open, setOpen] = useState(false);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const submitting = useRef(false);

  const close = () => {
    if (!submitting.current) setOpen(false);
  };

  const confirm = async () => {
    if (submitting.current || disabled) return;

    submitting.current = true;
    setPending(true);
    setError(null);

    try {
      await onConfirm();
      setOpen(false);
    } catch (error) {
      setError(error instanceof Error ? error.message : "Не удалось удалить. Попробуйте ещё раз.");
    } finally {
      submitting.current = false;
      setPending(false);
    }
  };

  return (
    <>
      <button
        type="button"
        className={className ?? styles.trigger}
        aria-label={ariaLabel}
        disabled={disabled || pending}
        onClick={() => {
          setError(null);
          setOpen(true);
        }}
      >
        {children}
      </button>
      <Modal open={open} title={title} onClose={close}>
        <p className={styles.description}>{description}</p>
        {error && (
          <p className={styles.error} role="alert">{error}</p>
        )}
        <div className={styles.actions}>
          <OutlineButton disabled={pending} onClick={close}>Отмена</OutlineButton>
          <Button disabled={disabled} loading={pending} onClick={() => void confirm()}>
            Удалить
          </Button>
        </div>
      </Modal>
    </>
  );
};

export default DeleteButton;
