import { AuditSummary, PlanSummary, type Expertise } from "@/entities/expertise";
import { formatRub } from "@/shared/lib/money";
import { DetailsRow } from "@/shared/ui/details-table";
import FilesList from "../files-list";

type AuditRowsProps = {
  expertise: Expertise;
};

const ATTACHMENT_KINDS = ["power_of_attorney", "sto", "opo_certificate", "company_card"];

const AuditRows = ({ expertise }: AuditRowsProps) => {
  const plans = expertise.documents.filter((item) => item.kind === "audit_plan");
  const attachments = expertise.documents.filter((item) => ATTACHMENT_KINDS.includes(item.kind));

  return (
    <>
      {expertise.audit_details && <AuditSummary details={expertise.audit_details} />}

      {expertise.offer_price && (
        <DetailsRow label="Цена аудитора">{formatRub(expertise.offer_price)}</DetailsRow>
      )}

      {expertise.counter_price && (
        <DetailsRow label="Встречная цена заказчика">{formatRub(expertise.counter_price)}</DetailsRow>
      )}

      <PlanSummary plan={expertise.audit_plan} team={expertise.team} />

      {plans.length > 0 && (
        <DetailsRow label="План аудита">
          <FilesList expertiseId={expertise.id} documents={plans} />
        </DetailsRow>
      )}

      {attachments.length > 0 && (
        <DetailsRow label="Приложения к заявке">
          <FilesList expertiseId={expertise.id} documents={attachments} />
        </DetailsRow>
      )}
    </>
  );
};

export default AuditRows;
