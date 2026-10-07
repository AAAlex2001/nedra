"use client";

import { ROLE_LABELS, updateProfile, useSession, type User } from "@/entities/user";
import { EmailRow, TextRow } from "@/features/account-settings";
import { formatDate } from "@/shared/lib/date";
import { DetailsRow, DetailsTable } from "@/shared/ui/details-table";

type AccountDetailsProps = {
  user: User;
};

const AccountDetails = ({ user }: AccountDetailsProps) => {
  const { signIn } = useSession();

  const saveName = async (fullName: string) => {
    signIn(await updateProfile({ full_name: fullName, phone: user.phone }));
  };

  const savePhone = async (phone: string) => {
    signIn(await updateProfile({ full_name: user.full_name, phone }));
  };

  return (
    <DetailsTable>
      <TextRow label="ФИО" value={user.full_name} onSave={saveName} />
      <EmailRow email={user.email} onChanged={signIn} />
      <TextRow label="Телефон" type="tel" inputMode="tel" value={user.phone} onSave={savePhone} />
      <DetailsRow label="Роль">{ROLE_LABELS[user.role]}</DetailsRow>
      <DetailsRow label="В сервисе с">{formatDate(user.created_at)}</DetailsRow>
    </DetailsTable>
  );
};

export default AccountDetails;
