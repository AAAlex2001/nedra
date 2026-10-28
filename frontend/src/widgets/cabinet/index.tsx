"use client";

import { useSearchParams } from "next/navigation";
import { ROLE_LABELS, useSession, type User } from "@/entities/user";
import { useAuthModal, useLogout } from "@/features/auth";
import { ActsTab, InvoicesTab } from "@/features/billing";
import { ExpertAttestation, useExpertProfile } from "@/features/expert-profile";
import {
  AssignedExpertises,
  IncomingExpertises,
  MyExpertises,
} from "@/features/expertise-cabinet";
import { NotificationsTab, useNotifications } from "@/features/notifications";
import Button from "@/shared/ui/button";
import Loader from "@/shared/ui/loader";
import SectionHeading from "@/shared/ui/section-heading";
import SidebarLayout from "@/shared/ui/sidebar-layout";
import Spinner from "@/shared/ui/spinner";
import { Tabs } from "@/shared/ui/tabs";
import { initials } from "./lib/initials";
import { sectionsFor, tabSections } from "./model/sections";
import AccountDetails from "./ui/account-details";
import { CabinetSidebar } from "./ui/cabinet-sidebar";
import styles from "./style.module.scss";

export { ServiceSidebar } from "./ui/cabinet-sidebar";

const TITLE = "Личный кабинет";

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
        <span>{user.email}</span>
        <span>{user.phone}</span>
      </span>
    </div>

    <div className={styles.controls}>
      {user.role === "customer" && (
        <>
          <Button href="/blits-ekspert" className={styles.newOrder}>
            Новая ЭПБ
          </Button>
          <Button href="/blits-audit" className={styles.newOrder}>
            Новый аудит
          </Button>
        </>
      )}
      <button type="button" className={styles.logout} disabled={pending} onClick={onLogout}>
        {pending ? <Spinner size={14} /> : "Выйти"}
      </button>
    </div>
  </div>
);

type PanelProps = {
  user: User;
  tab: string;
  notifications: ReturnType<typeof useNotifications>;
};

const ExpertPanel = ({ user, tab, notifications }: PanelProps) => {
  const { state, replaceProfile } = useExpertProfile();

  if (state.status === "loading") {
    return <Loader />;
  }

  if (state.status === "error") {
    return <p className={styles.error}>{state.message}</p>;
  }

  return (
    <>
      {tab === "incoming" && <IncomingExpertises certificates={state.profile.certificates} />}
      {tab === "assigned" && <AssignedExpertises kind="active" />}
      {tab === "finished" && <AssignedExpertises kind="finished" />}
      {tab === "notifications" && <NotificationsTab notifications={notifications} />}
      {tab === "account" && (
        <>
          <AccountDetails user={user} />
          <ExpertAttestation
            profile={state.profile}
            catalog={state.catalog}
            onChange={replaceProfile}
          />
        </>
      )}
    </>
  );
};

const CustomerPanel = ({ user, tab, notifications }: PanelProps) => (
  <>
    {tab === "mine" && <MyExpertises kind="active" />}
    {tab === "finished" && <MyExpertises kind="finished" />}
    {tab === "invoices" && <InvoicesTab />}
    {tab === "acts" && <ActsTab />}
    {tab === "notifications" && <NotificationsTab notifications={notifications} />}
    {tab === "account" && <AccountDetails user={user} />}
  </>
);

type UserCabinetProps = {
  user: User;
};

const UserCabinet = ({ user }: UserCabinetProps) => {
  const searchParams = useSearchParams();
  const notifications = useNotifications();
  const { logout, pending } = useLogout();

  const tabs = tabSections(sectionsFor(user.role));
  const requestedTab = tabs.find((item) => item.key === searchParams.get("tab"));
  const tab = requestedTab ? requestedTab.key : tabs[0].key;

  const tabItems = tabs.map((item) => ({
    key: item.key,
    label: item.label,
    badge: item.key === "notifications" ? notifications.unread : undefined,
  }));

  const showTab = (key: string) => window.history.replaceState(null, "", `?tab=${key}`);

  return (
    <SidebarLayout sidebar={<CabinetSidebar active={tab} unread={notifications.unread} />}>
      <SectionHeading title={TITLE} />

      <div className={styles.cabinet}>
        <ProfileBar user={user} pending={pending} onLogout={() => void logout()} />

        <div className={styles.tabs}>
          <Tabs items={tabItems} active={tab} onSelect={showTab} label="Разделы кабинета" stretch />
        </div>

        <section className={styles.panel}>
          {user.role === "expert" ? (
            <ExpertPanel user={user} tab={tab} notifications={notifications} />
          ) : (
            <CustomerPanel user={user} tab={tab} notifications={notifications} />
          )}
        </section>
      </div>
    </SidebarLayout>
  );
};

const Cabinet = () => {
  const session = useSession();
  const { openModal } = useAuthModal();

  if (session.status === "anonymous" || !session.user) {
    return (
      <>
        <SectionHeading title={TITLE} />
        <div className={styles.locked}>
          <p className={styles.lockedTitle}>Войдите, чтобы открыть личный кабинет</p>
          <p className={styles.lockedText}>
            В кабинете заказчик отправляет документацию на экспертизу, а эксперт
            принимает заявки и выдаёт заключения.
          </p>
          <Button onClick={openModal}>Вход / Регистрация</Button>
        </div>
      </>
    );
  }

  return <UserCabinet user={session.user} />;
};

export default Cabinet;
