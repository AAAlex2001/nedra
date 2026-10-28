"use client";

import classNames from "classnames";
import { useEffect, useState } from "react";
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
  const [hidden, setHidden] = useState(false);

  useEffect(() => {
    let previousY = window.scrollY;

    const onScroll = () => {
      const currentY = window.scrollY;

      setHidden(currentY > previousY);
      previousY = currentY;
    };

    window.addEventListener("scroll", onScroll, { passive: true });

    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  if (status !== "anonymous") return null;

  return (
    <div className={classNames(styles.bar, hidden && styles.hidden)}>
      <Button className={styles.button} onClick={start}>
        {text}
      </Button>
    </div>
  );
};

export default StickyStart;
