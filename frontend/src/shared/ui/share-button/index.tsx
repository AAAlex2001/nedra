"use client";

import { useState } from "react";
import styles from "./style.module.scss";

type ShareButtonProps = {
  title: string;
};

const ShareButton = ({ title }: ShareButtonProps) => {
  const [copied, setCopied] = useState(false);

  const share = async () => {
    const url = window.location.href;

    if (navigator.share) {
      try {
        await navigator.share({ title, url });
        return;
      } catch {
        return;
      }
    }

    await navigator.clipboard.writeText(url);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button type="button" className={styles.button} onClick={() => void share()}>
      {copied ? "Ссылка скопирована" : "Поделиться"}
    </button>
  );
};

export default ShareButton;
