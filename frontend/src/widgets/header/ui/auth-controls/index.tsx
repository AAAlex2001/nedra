"use client";

import Link from "next/link";
import { useSession } from "@/entities/user";
import { useAuthModal } from "@/features/auth";
import Button from "@/shared/ui/button";
import NotificationsBell from "../notifications-bell";
import styles from "./style.module.scss";

const initials = (fullName: string): string => {
  const parts = fullName.trim().split(" ").filter((part) => part !== "");
  const letters = parts.slice(0, 2).map((part) => part[0].toUpperCase());

  return letters.join("");
};

const AuthControls = () => {
  const session = useSession();
  const { openModal } = useAuthModal();

  if (session.status === "anonymous" || !session.user) {
    return (
      <Button className={styles.login} onClick={openModal}>
        Вход / Регистрация
      </Button>
    );
  }

  return (
    <div className={styles.account}>
      <NotificationsBell />

      <Link href="/kabinet" className={styles.user} title="Личный кабинет">
        <span className={styles.avatar} aria-hidden="true">
          {initials(session.user.full_name)}
        </span>
        <span className={styles.name}>Личный кабинет</span>
      </Link>
    </div>
  );
};

export default AuthControls;
