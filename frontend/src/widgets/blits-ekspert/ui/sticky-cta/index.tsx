"use client";

import { useAuthModal } from "@/features/auth";
import Button from "@/shared/ui/button";
import styles from "./style.module.scss";

const StickyCta = () => {
  const { openModal } = useAuthModal();

  return (
    <div className={styles.bar}>
      <Button className={styles.button} onClick={openModal}>
        Отправить документацию
      </Button>
    </div>
  );
};

export default StickyCta;
