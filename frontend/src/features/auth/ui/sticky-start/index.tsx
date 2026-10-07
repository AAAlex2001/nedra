"use client";

import Button from "@/shared/ui/button";
import { useStartAction } from "../../model/use-start-action";
import styles from "./style.module.scss";

type StickyStartProps = {
  text: string;
};

const StickyStart = ({ text }: StickyStartProps) => {
  const start = useStartAction();

  return (
    <div className={styles.bar}>
      <Button className={styles.button} onClick={start}>
        {text}
      </Button>
    </div>
  );
};

export default StickyStart;
