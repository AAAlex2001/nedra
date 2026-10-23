"use client";

import Button from "@/shared/ui/button";
import { useSession } from "@/entities/user";
import { useStartAction } from "../../model/use-start-action";
import styles from "./style.module.scss";

type StickyStartProps = {
  text: string;
};

const StickyStart = ({ text }: StickyStartProps) => {
  const { status } = useSession();
  const start = useStartAction();

  if (status !== "anonymous") return null;

  return (
    <div className={styles.bar}>
      <Button className={styles.button} onClick={start}>
        {text}
      </Button>
    </div>
  );
};

export default StickyStart;
