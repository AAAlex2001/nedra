"use client";

import Link from "next/link";
import type { ExpertCatalog } from "@/entities/expert";
import { useSession } from "@/entities/user";
import { useAuthModal } from "@/features/auth";
import { OrderForm } from "@/features/expertise-order";
import Button from "@/shared/ui/button";
import styles from "./style.module.scss";

type ExpertiseOrderProps = {
  catalog: ExpertCatalog | null;
};

const ExpertiseOrder = ({ catalog }: ExpertiseOrderProps) => {
  const session = useSession();
  const { openModal } = useAuthModal();

  if (!catalog) {
    return <p className={styles.error}>Не удалось загрузить справочник. Обновите страницу.</p>;
  }

  if (session.status === "anonymous" || !session.user) {
    return (
      <div className={styles.locked}>
        <p className={styles.lockedTitle}>Чтобы отправить документацию, войдите как заказчик</p>
        <p className={styles.lockedText}>
          Регистрация занимает минуту. После входа заявка уйдёт экспертам, аттестованным
          по вашей отрасли.
        </p>
        <Button onClick={openModal}>Вход / Регистрация</Button>
      </div>
    );
  }

  if (session.user.role === "expert") {
    return (
      <div className={styles.locked}>
        <p className={styles.lockedTitle}>Вы вошли как эксперт</p>
        <p className={styles.lockedText}>
          Документацию отправляют заказчики. Входящие заявки по вашей аттестации ждут в{" "}
          <Link href="/kabinet" className={styles.link}>
            личном кабинете
          </Link>
          .
        </p>
      </div>
    );
  }

  return <OrderForm catalog={catalog} />;
};

export default ExpertiseOrder;
