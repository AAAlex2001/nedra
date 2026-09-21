"use client";

import { useAuthModal } from "@/features/auth";
import Button from "@/shared/ui/button";
import styles from "./style.module.scss";

type StartButtonsProps = {
  secondaryHref: string;
  secondaryText: string;
};

const StartButtons = ({ secondaryHref, secondaryText }: StartButtonsProps) => {
  const { openModal } = useAuthModal();

  return (
    <>
      <Button onClick={openModal}>Отправить документацию</Button>
      <a className={styles.secondary} href={secondaryHref}>
        {secondaryText}
      </a>
    </>
  );
};

export default StartButtons;
