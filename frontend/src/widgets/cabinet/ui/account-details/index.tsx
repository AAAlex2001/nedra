import { ROLE_LABELS, type User } from "@/entities/user";
import { formatDate } from "@/shared/lib/date";
import { DetailsRow, DetailsTable } from "@/shared/ui/details-table";

type AccountDetailsProps = {
  user: User;
};

const AccountDetails = ({ user }: AccountDetailsProps) => (
  <DetailsTable>
    <DetailsRow label="ФИО">{user.full_name}</DetailsRow>
    <DetailsRow label="Email">{user.email}</DetailsRow>
    <DetailsRow label="Телефон">{user.phone}</DetailsRow>
    <DetailsRow label="Роль">{ROLE_LABELS[user.role]}</DetailsRow>
    <DetailsRow label="В сервисе с">{formatDate(user.created_at)}</DetailsRow>
  </DetailsTable>
);

export default AccountDetails;
