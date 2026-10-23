"use client";

import Button from "@/shared/ui/button";
import { useStartAction } from "../../model/use-start-action";
import styles from "./style.module.scss";

type StickyStartProps = {
  text: string;
  secondaryText?: string;
};

const StickyStart = ({ text, secondaryText }: StickyStartProps) => {
  const start = useStartAction();

  return (
    <div className={styles.bar}>
      <Button className={styles.button} onClick={start}>
        {text}
      </Button>
      {secondaryText && (
        <a className={styles.secondary} href="#stoimost">
          {secondaryText}
        </a>
      )}
    </div>
  );
};

export default StickyStart;
