"use client";

import {
  AUDIT_FILES_ACCEPT,
  AuditChecklist,
  type AuditChecklistItem,
} from "@/entities/expertise";
import TextField from "@/shared/ui/text-field";
import { useAuditOrder } from "../../model/use-audit-order";
import AuditDetails from "../audit-details";
import CustomerSection from "../customer-section";
import OrderShell from "../order-shell";

type AuditFormProps = {
  checklist: AuditChecklistItem[];
};

const CHECKLIST_NOTE =
  "Загрузите имеющиеся документы сейчас или после согласования Плана аудита. Аудитор проанализирует комплектность и направит запрос на недостающие сведения. Принимаются PDF, файлы электронной подписи, фото и видео.";

const AuditForm = ({ checklist }: AuditFormProps) => {
  const audit = useAuditOrder();
  const { order } = audit;

  return (
    <OrderShell
      order={order}
      executors="Аудиторы"
      submitText="Отправить на аудит"
      errors={audit.errors}
      onSubmit={audit.submit}
    >
      <AuditDetails
        form={audit.form}
        errors={audit.errors}
        onChange={audit.changeForm}
        price={order.state.price}
        onPriceChange={order.changePrice}
      />

      <AuditChecklist
        checklist={checklist}
        files={order.state.auditFiles}
        note={CHECKLIST_NOTE}
        onAdd={audit.addFiles}
        onRemove={audit.removeFile}
      />

      <CustomerSection order={order} errors={audit.errors} cardAccept={AUDIT_FILES_ACCEPT} />

      <TextField
        label="Комментарий"
        multiline
        placeholder="Что важно знать аудитору: структура организации, количество ОПО, на что обратить внимание"
        maxLength={4000}
        value={order.state.comment}
        onChange={order.changeComment}
      />
    </OrderShell>
  );
};

export default AuditForm;
