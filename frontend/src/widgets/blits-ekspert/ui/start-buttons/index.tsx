"use client";

import Button from "@/shared/ui/button";
import { useStartAction } from "../../model/use-start-action";
import styles from "./style.module.scss";

type StartButtonsProps = {
  secondaryHref: string;
  secondaryText: string;
};

const StartButtons = ({ secondaryHref, secondaryText }: StartButtonsProps) => {
  const start = useStartAction();

  return (
    <>
      <Button onClick={start}>Отправить документацию</Button>
      <a className={styles.secondary} href={secondaryHref}>
        {secondaryText}
      </a>
    </>
  );
};

export default StartButtons;
