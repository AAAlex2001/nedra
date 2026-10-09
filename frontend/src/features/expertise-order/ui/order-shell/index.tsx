"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import Button from "@/shared/ui/button";
import Modal from "@/shared/ui/modal";
import type { FormErrors } from "../../model/types";
import type { Order } from "../../model/use-order";
import styles from "./style.module.scss";

type OrderShellProps = {
  order: Order;
  executors: string;
  submitText: string;
  errors: FormErrors;
  onSubmit: () => Promise<void>;
  children: ReactNode;
};

const OrderShell = ({
  order,
  executors,
  submitText,
  errors,
  onSubmit,
  children,
}: OrderShellProps) => {
  const [firstError] = Object.values(errors);

  return (
    <form
      className={styles.form}
      noValidate
      onSubmit={(event) => {
        event.preventDefault();
        void onSubmit();
      }}
    >
      <Modal open={order.state.status === "success"} title="Заявка отправлена" onClose={order.closeSuccess}>
        <p className={styles.successText}>
          {executors} получили уведомление. Когда кто-то из них возьмёт заявку в работу, вы увидите
          это в{" "}
          <Link href="/kabinet" className={styles.successLink}>
            личном кабинете
          </Link>
          .
        </p>
      </Modal>

      {children}

      {firstError && (
        <p className={styles.error}>{firstError}. Проверьте поля, выделенные красным.</p>
      )}

      {order.state.error && <p className={styles.error}>{order.state.error}</p>}

      <Button type="submit" className={styles.submit} loading={order.state.status === "loading"}>
        {submitText}
      </Button>
    </form>
  );
};

export default OrderShell;
