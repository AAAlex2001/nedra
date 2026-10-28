"use client";

import Link from "next/link";
import { useEffect, useRef, type FormEvent, type ReactNode } from "react";
import Button from "@/shared/ui/button";
import Modal from "@/shared/ui/modal";
import OutlineButton from "@/shared/ui/outline-button";
import type { FormErrors } from "../../model/types";
import type { Order } from "../../model/use-order";
import type { Steps } from "../../model/use-steps";
import OrderSteps from "../order-steps";
import styles from "./style.module.scss";

type OrderShellProps = {
  order: Order;
  steps: Steps;
  executors: string;
  submitText: string;
  errors: FormErrors;
  onSubmit: () => Promise<void>;
  children: ReactNode;
  theme?: string;
};

const OrderShell = ({
  order,
  steps,
  executors,
  submitText,
  errors,
  onSubmit,
  children,
  theme,
}: OrderShellProps) => {
  const formRef = useRef<HTMLFormElement>(null);
  const shownIndex = useRef(steps.index);
  const [firstError] = Object.values(errors);

  useEffect(() => {
    if (shownIndex.current === steps.index) return;

    shownIndex.current = steps.index;
    formRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, [steps.index]);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (steps.isLast) {
      void onSubmit();
      return;
    }

    steps.next();
  };

  return (
    <form ref={formRef} className={styles.form} noValidate onSubmit={handleSubmit}>
      <Modal
        open={order.state.status === "success"}
        title="Заявка отправлена"
        className={theme}
        onClose={order.closeSuccess}
      >
        <p className={styles.successText}>
          {executors} получили уведомление. Когда кто-то из них возьмёт заявку в работу, вы увидите
          это в{" "}
          <Link href="/kabinet" className={styles.successLink}>
            личном кабинете
          </Link>
          .
        </p>
      </Modal>

      <OrderSteps steps={steps} theme={theme} />

      {children}

      {firstError && (
        <p className={styles.error}>{firstError}. Проверьте поля, выделенные красным.</p>
      )}

      {order.state.error && <p className={styles.error}>{order.state.error}</p>}

      <div className={styles.nav}>
        {!steps.isFirst && <OutlineButton onClick={steps.back}>Назад</OutlineButton>}

        <Button type="submit" className={styles.next} loading={order.state.status === "loading"}>
          {steps.isLast ? submitText : "Далее"}
        </Button>
      </div>
    </form>
  );
};

export default OrderShell;
