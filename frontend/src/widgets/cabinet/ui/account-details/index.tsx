import type { User } from "@/entities/user";
import { formatDate } from "@/shared/lib/date";
import { DetailsRow, DetailsTable } from "@/shared/ui/details-table";

type AccountDetailsProps = {
  user: User;
};

const roles = (user: User): string => (user.is_expert ? "Заказчик и эксперт" : "Заказчик");

const AccountDetails = ({ user }: AccountDetailsProps) => (
  <DetailsTable>
    <DetailsRow label="ФИО">{user.full_name}</DetailsRow>
    <DetailsRow label="Email">{user.email}</DetailsRow>
    <DetailsRow label="Телефон">{user.phone}</DetailsRow>
    <DetailsRow label="Доступные роли">{roles(user)}</DetailsRow>
    <DetailsRow label="В сервисе с">{formatDate(user.created_at)}</DetailsRow>
  </DetailsTable>
);

export default AccountDetails;
