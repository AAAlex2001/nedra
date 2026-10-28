"use client";

import classNames from "classnames";
import Link from "next/link";
import { ROLE_LABELS, useSession } from "@/entities/user";
import { useLogout } from "@/features/auth";
import { useNotifications } from "@/features/notifications";
import Spinner from "@/shared/ui/spinner";
import { initials } from "../../lib/initials";
import {
  SECTION_GROUPS,
  sectionHref,
  sectionsFor,
  type CabinetSection,
} from "../../model/sections";
import SectionIcon from "./section-icon";
import styles from "./style.module.scss";

type CabinetSidebarProps = {
  active: string;
  unread: number;
};

type SectionLinkProps = {
  section: CabinetSection;
  active: boolean;
  unread: number;
};

const SectionLink = ({ section, active, unread }: SectionLinkProps) => {
  const showBadge = section.key === "notifications" && unread > 0;

  return (
    <Link
      href={sectionHref(section)}
      className={classNames(styles.item, active && styles.itemActive)}
      aria-current={active ? "page" : undefined}
    >
      <SectionIcon icon={section.icon} />
      <span className={styles.label}>{section.label}</span>
      {showBadge && <span className={styles.badge}>{unread > 99 ? "99+" : unread}</span>}
    </Link>
  );
};

export const CabinetSidebar = ({ active, unread }: CabinetSidebarProps) => {
  const { user } = useSession();
  const { logout, pending } = useLogout();

  if (!user) return null;

  const sections = sectionsFor(user.role);

  return (
    <nav className={styles.sidebar} aria-label="Разделы кабинета">
      <div className={styles.profile}>
        <span className={styles.avatar} aria-hidden="true">
          {initials(user.full_name)}
        </span>
        <span className={styles.identity}>
          <span className={styles.name}>{user.full_name}</span>
          <span className={styles.role}>{ROLE_LABELS[user.role]}</span>
        </span>
      </div>

      {SECTION_GROUPS.map((group) => {
        const groupSections = sections.filter((section) => section.group === group);

        if (groupSections.length === 0) return null;

        return (
          <div key={group} className={styles.group}>
            <span className={styles.groupTitle}>{group}</span>
            {groupSections.map((section) => (
              <SectionLink
                key={section.key}
                section={section}
                active={section.key === active}
                unread={unread}
              />
            ))}
          </div>
        );
      })}

      <button
        type="button"
        className={classNames(styles.item, styles.logout)}
        disabled={pending}
        onClick={() => void logout()}
      >
        {pending ? <Spinner size={18} /> : <SectionIcon icon="logout" />}
        <span className={styles.label}>Выйти</span>
      </button>
    </nav>
  );
};

type ServiceSidebarProps = {
  active: string;
};

export const ServiceSidebar = ({ active }: ServiceSidebarProps) => {
  const notifications = useNotifications();

  return <CabinetSidebar active={active} unread={notifications.unread} />;
};
