"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef } from "react";
import { CloseIcon, NedraLogo, InfoIcon, DocumentIcon, PeopleIcon, GraduationIcon, MailIcon, PencilIcon, GlobeIcon, PhoneIcon, OfficialCertificateIcon } from "@/shared/ui/icons";
import ServiceNavigation from "@/widgets/service-navigation";
import type { HeaderNavItem } from "../../data";
import styles from "./style.module.scss";
const ICONS = [InfoIcon, DocumentIcon, PeopleIcon, OfficialCertificateIcon, GraduationIcon, GlobeIcon, PencilIcon, MailIcon, PhoneIcon];
type BurgerMenuProps = { open: boolean; nav: HeaderNavItem[]; onClose: () => void };
const BurgerMenu = ({ open, nav, onClose }: BurgerMenuProps) => {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const pathname = usePathname();
  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;
    if (!open) { if (dialog.open) dialog.close(); return; }
    if (!dialog.open) dialog.showModal();
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => { document.body.style.overflow = previousOverflow; };
  }, [open]);
  return (
    <dialog ref={dialogRef} className={styles.drawer} aria-label="Меню НПИ «Недра»" onCancel={onClose} onClose={onClose} onClick={(event) => { if (event.target === event.currentTarget) onClose(); }}>
      <div className={styles.content}>
        <header className={styles.header}>
          <Link href="/" onClick={onClose} aria-label="НПИ «Недра» — на главную"><NedraLogo className={styles.logo} /></Link>
          <button type="button" className={styles.close} onClick={onClose} aria-label="Закрыть меню"><CloseIcon /></button>
        </header>
        <nav className={styles.nav} aria-label="Основные разделы">
          <ServiceNavigation onNavigate={onClose} />
          <div className={styles.group}>
            <span className={styles.groupTitle}>Разделы</span>
            <div className={styles.grid}>
              {nav.map((item, index) => {
                const Icon = ICONS[index] ?? DocumentIcon;
                const active = !item.href.includes("#") && (pathname === item.href || pathname.startsWith(item.href + "/"));
                return <Link key={item.href} className={styles.tile} href={item.href} onClick={onClose} aria-current={active ? "page" : undefined}><Icon /><span>{item.label}</span></Link>;
              })}
            </div>
          </div>
        </nav>
      </div>
    </dialog>
  );
};
export default BurgerMenu;
