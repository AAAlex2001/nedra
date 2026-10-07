"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { useSession } from "@/entities/user";
import Button from "@/shared/ui/button";
import { useAuthModal } from "../../model/auth-modal-context";
import styles from "./style.module.scss";

type CustomerGateProps = {
  title: string;
  text: string;
  children: ReactNode;
};

const CustomerGate = ({ title, text, children }: CustomerGateProps) => {
  const session = useSession();
  const { openModal } = useAuthModal();

  if (session.status === "anonymous" || !session.user) {
    return (
      <div className={styles.locked}>
        <p className={styles.title}>{title}</p>
        <p className={styles.text}>{text}</p>
        <Button onClick={openModal}>Вход / Регистрация</Button>
      </div>
    );
  }

  if (session.user.role === "expert") {
    return (
      <div className={styles.locked}>
        <p className={styles.title}>Вы вошли как эксперт</p>
        <p className={styles.text}>
          Документы отправляют заказчики. Входящие заявки по вашей аттестации ждут в{" "}
          <Link href="/kabinet" className={styles.link}>
            личном кабинете
          </Link>
          .
        </p>
      </div>
    );
  }

  return children;
};

export default CustomerGate;
