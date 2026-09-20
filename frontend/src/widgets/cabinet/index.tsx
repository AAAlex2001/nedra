"use client";

import { useState } from "react";
import { ROLE_LABELS, useSession, type User } from "@/entities/user";
import { useAuthModal, useLogout } from "@/features/auth";
import { ActsTab, CompanyForm, InvoicesTab } from "@/features/billing";
import { ExpertAttestation, useExpertProfile } from "@/features/expert-profile";
import {
  AssignedExpertises,
  IncomingExpertises,
  MyExpertises,
} from "@/features/expertise-cabinet";
import Button from "@/shared/ui/button";
import Loader from "@/shared/ui/loader";
import Spinner from "@/shared/ui/spinner";
import { Tabs } from "@/shared/ui/tabs";
import AccountDetails from "./ui/account-details";
import styles from "./style.module.scss";

const initials = (fullName: string): string => {
  const parts = fullName.trim().split(" ").filter((part) => part !== "");
  const letters = parts.slice(0, 2).map((part) => part[0].toUpperCase());

  return letters.join("");
};

type ProfileBarProps = {
  user: User;
  pending: boolean;
  onLogout: () => void;
};

const ProfileBar = ({ user, pending, onLogout }: ProfileBarProps) => (
  <div className={styles.profile}>
    <span className={styles.avatar} aria-hidden="true">
      {initials(user.full_name)}
    </span>

    <div className={styles.identity}>
      <div className={styles.nameRow}>
        <span className={styles.name}>{user.full_name}</span>
        <span className={styles.role}>{ROLE_LABELS[user.role]}</span>
      </div>
      <span className={styles.contacts}>
        {user.email} · {user.phone}
      </span>
    </div>

    <div className={styles.controls}>
      <button type="button" className={styles.logout} disabled={pending} onClick={onLogout}>
        {pending ? <Spinner size={14} /> : "Выйти"}
      </button>
    </div>
  </div>
);

const EXPERT_TABS = [
  { key: "incoming", label: "Входящие заявки" },
  { key: "assigned", label: "В работе" },
  { key: "account", label: "Мои данные" },
];

const CUSTOMER_TABS = [
  { key: "mine", label: "Мои экспертизы" },
  { key: "invoices", label: "Счета" },
  { key: "acts", label: "Акты" },
  { key: "account", label: "Мои данные" },
];

type CabinetPanelProps = {
  user: User;
};

const ExpertCabinet = ({ user }: CabinetPanelProps) => {
  const [tab, setTab] = useState("incoming");
  const state = useExpertProfile();

  if (state.status === "loading") {
    return <Loader />;
  }

  if (state.status === "error") {
    return <p className={styles.error}>{state.message}</p>;
  }

  return (
    <>
      <Tabs items={EXPERT_TABS} active={tab} onSelect={setTab} label="Разделы кабинета" />

      <section className={styles.panel}>
        {tab === "incoming" && <IncomingExpertises certificates={state.profile.certificates} />}
        {tab === "assigned" && <AssignedExpertises />}
        {tab === "account" && (
          <>
            <AccountDetails user={user} />
            <ExpertAttestation profile={state.profile} catalog={state.catalog} />
          </>
        )}
      </section>
    </>
  );
};

const CustomerCabinet = ({ user }: CabinetPanelProps) => {
  const [tab, setTab] = useState("mine");

  return (
    <>
      <div className={styles.toolbar}>
        <Tabs items={CUSTOMER_TABS} active={tab} onSelect={setTab} label="Разделы кабинета" />
        {tab === "mine" && <Button href="/blits-ekspert">Новая заявка</Button>}
      </div>

      <section className={styles.panel}>
        {tab === "mine" && <MyExpertises />}
        {tab === "invoices" && <InvoicesTab />}
        {tab === "acts" && <ActsTab />}
        {tab === "account" && (
          <>
            <AccountDetails user={user} />
            <CompanyForm />
          </>
        )}
      </section>
    </>
  );
};

const Cabinet = () => {
  const session = useSession();
  const { openModal } = useAuthModal();
  const { logout, pending } = useLogout();

  if (session.status === "anonymous" || !session.user) {
    return (
      <div className={styles.locked}>
        <p className={styles.lockedTitle}>Войдите, чтобы открыть личный кабинет</p>
        <p className={styles.lockedText}>
          В кабинете заказчик отправляет документацию на экспертизу, а эксперт
          принимает заявки и выдаёт заключения.
        </p>
        <Button onClick={openModal}>Вход / Регистрация</Button>
      </div>
    );
  }

  const user = session.user;

  return (
    <div className={styles.cabinet}>
      <ProfileBar user={user} pending={pending} onLogout={() => void logout()} />

      {user.role === "expert" ? <ExpertCabinet user={user} /> : <CustomerCabinet user={user} />}
    </div>
  );
};

export default Cabinet;
