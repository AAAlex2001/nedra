"use client";

import Button from "@/shared/ui/button";
import { useStartAction } from "../../model/use-start-action";
import styles from "./style.module.scss";

const StickyCta = () => {
  const start = useStartAction();

  return (
    <div className={styles.bar}>
      <Button className={styles.button} onClick={start}>
        Отправить документацию
      </Button>
    </div>
  );
};

export default StickyCta;
