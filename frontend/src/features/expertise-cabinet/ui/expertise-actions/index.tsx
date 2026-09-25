"use client";

import { useState, type ReactNode } from "react";
import { invoicePdfUrl, type PaymentDocumentKind } from "@/entities/billing";
import {
  cardPaymentAllowed,
  contractKindsFor,
  type ContractKind,
  type Expertise,
} from "@/entities/expertise";
import { formatRequestDate } from "@/entities/request";
import { formatRub, halfOf } from "@/shared/lib/money";
import Button from "@/shared/ui/button";
import { CheckIcon, ClockIcon } from "@/shared/ui/icons";
import { useExpertiseActions } from "../../model/use-expertise-actions";
import ConclusionForm from "../conclusion-form";
import ContractConsent from "../contract-consent";
import ContractKindPicker from "../contract-kind-picker";
import PaymentProofForm from "../payment-proof-form";
import RemarksForm from "../remarks-form";
import RevisionForm from "../revision-form";
import styles from "./style.module.scss";

type ExpertiseActionsProps = {
  expertise: Expertise;
  role: "customer" | "expert";
  onChange: (item: Expertise) => void;
};

type Step = {
  text: string;
  action?: ReactNode;
  form?: ReactNode;
};

const when = (value: string | null): string => (value ? formatRequestDate(value) : "");

const PROOF_BUTTONS: { kind: PaymentDocumentKind; label: string }[] = [
  { kind: "payment_order", label: "Я оплатил" },
  { kind: "guarantee_letter", label: "Гарантийное письмо" },
];

const ExpertiseActions = ({ expertise, role, onChange }: ExpertiseActionsProps) => {
  const actions = useExpertiseActions(expertise, onChange);
  const [remarksOpen, setRemarksOpen] = useState(false);
  const [proofKind, setProofKind] = useState<PaymentDocumentKind | null>(null);
  const [sentKind, setSentKind] = useState<PaymentDocumentKind | null>(null);
  const [contractKind, setContractKind] = useState<ContractKind | null>(expertise.contract_kind);

  const half = formatRub(halfOf(expertise.price));
  const price = formatRub(expertise.price);
  const invoice = expertise.invoice;
  const canReport = invoice !== null && invoice.reported_at === null;
  const guaranteed =
    sentKind === "guarantee_letter" ||
    expertise.documents.some((item) => item.kind === "guarantee_letter");
  const cardAllowed = cardPaymentAllowed(expertise);
  const kindUnknown = expertise.contract_kind === null;

  const toggleProof = (kind: PaymentDocumentKind) =>
    setProofKind(proofKind === kind ? null : kind);

  const payment = (hasPayment: boolean) => (
    <div className={styles.payment}>
      <div className={styles.payButtons}>
        {cardAllowed && (
          <Button
            className={styles.payCard}
            loading={actions.pending}
            onClick={() => void actions.pay()}
          >
            Оплатить картой {half}
          </Button>
        )}

        {invoice === null ? (
          <button
            type="button"
            className={styles.secondary}
            disabled={actions.pending}
            onClick={() => void actions.requestInvoice()}
          >
            Счёт для юрлица
          </button>
        ) : (
          <a
            className={styles.secondary}
            href={invoicePdfUrl(invoice.id)}
            target="_blank"
            rel="noreferrer"
          >
            Счёт № {invoice.number}
          </a>
        )}

        {canReport &&
          PROOF_BUTTONS.map((item) => (
            <button
              key={item.kind}
              type="button"
              className={`${styles.secondary} ${proofKind === item.kind ? styles.secondaryActive : ""}`}
              disabled={actions.pending}
              onClick={() => toggleProof(item.kind)}
            >
              {item.label}
            </button>
          ))}

        {hasPayment && (
          <button
            type="button"
            className={styles.secondary}
            disabled={actions.pending}
            onClick={() => void actions.refresh()}
          >
            Проверить оплату
          </button>
        )}
      </div>

      {canReport && proofKind !== null && (
        <div className={styles.proof}>
          <PaymentProofForm
            key={proofKind}
            kind={proofKind}
            pending={actions.pending}
            onSubmit={(document) => {
              setProofKind(null);
              setSentKind(proofKind);
              void actions.reportPaid(document, proofKind);
            }}
          />
        </div>
      )}
    </div>
  );

  const customerStep = (): Step => {
    switch (expertise.status) {
      case "new":
        return { text: "Ждём, когда эксперт по вашей области возьмёт заявку" };

      case "expert_ready":
        return {
          text: `${expertise.expert_name} готов провести экспертизу за ${price}, оплата двумя частями по 50 %. Прочитайте договор и соглашение о конфиденциальности и подпишите их`,
          form: (
            <ContractConsent
              expertiseId={expertise.id}
              pending={actions.pending}
              onSign={() => void actions.confirm()}
            />
          ),
        };

      case "contract":
        return {
          text: cardAllowed
            ? `Договор заключён ${when(expertise.contract_at)}. Оплатите аванс, и эксперт приступит к работе`
            : `Договор заключён ${when(expertise.contract_at)}. Оплатите аванс по счёту исполнителя и приложите платёжное поручение`,
          form: payment(expertise.advance_payment !== null),
        };

      case "in_progress":
        return { text: `Аванс оплачен ${when(expertise.advance_paid_at)}. Эксперт работает над заключением` };

      case "remarks":
        return {
          text: "Эксперт прислал замечания. Внесите изменения в документацию и отправьте её повторно",
          form: <RevisionForm pending={actions.pending} onSubmit={actions.submitRevision} />,
        };

      case "conclusion_ready":
        return {
          text: "Замечаний нет, заключение готово. Требуется полная оплата: внесите остаток, и эксперт отправит подписанный документ",
          form: payment(expertise.final_payment !== null),
        };

      case "paid":
        return { text: `Остаток оплачен ${when(expertise.final_paid_at)}. Эксперт подписывает заключение ЭЦП` };

      case "sent":
        return {
          text: `Заключение отправлено ${when(expertise.sent_at)}. Скачайте файлы и примите работу`,
          action: (
            <Button loading={actions.pending} onClick={() => void actions.finish()}>
              Работа принята
            </Button>
          ),
        };

      case "accepted":
        return { text: `Работа принята ${when(expertise.accepted_at)}` };
    }
  };

  const expertStep = (): Step => {
    switch (expertise.status) {
      case "new":
        return {
          text: kindUnknown
            ? `Стоимость экспертизы ${price}. Заказчик не знает вид проекта: определите его по документации, от него зависит договор`
            : `Стоимость экспертизы ${price}. Заявку получит первый, кто подтвердит готовность`,
          action: (
            <Button
              disabled={contractKind === null}
              loading={actions.pending}
              onClick={() => void actions.accept(contractKind)}
            >
              Готов провести экспертизу
            </Button>
          ),
          form: kindUnknown ? (
            <ContractKindPicker
              kinds={contractKindsFor(expertise.object_code)}
              value={contractKind}
              onChange={setContractKind}
            />
          ) : null,
        };

      case "expert_ready":
        return { text: `Вы подтвердили готовность ${when(expertise.expert_ready_at)}. Ждём согласия заказчика` };

      case "contract":
        return { text: `Договор заключён ${when(expertise.contract_at)}. Ждём аванс от заказчика` };

      case "in_progress":
        return {
          text: "Документация у вас. Если замечаний нет, отметьте, что заключение готово, иначе пришлите рекомендации по приведению объекта в соответствие",
          action: remarksOpen ? null : (
            <>
              <button
                type="button"
                className={styles.secondary}
                disabled={actions.pending}
                onClick={() => setRemarksOpen(true)}
              >
                Есть замечания
              </button>
              <Button loading={actions.pending} onClick={() => void actions.conclusionReady()}>
                Заключение готово
              </Button>
            </>
          ),
          form: remarksOpen ? (
            <RemarksForm
              pending={actions.pending}
              onSubmit={actions.submitRemarks}
              onCancel={() => setRemarksOpen(false)}
            />
          ) : null,
        };

      case "remarks":
        return { text: "Замечания отправлены. Ждём исправленную документацию от заказчика" };

      case "conclusion_ready":
        return { text: "Ждём оплату остатка от заказчика" };

      case "paid":
        return {
          text: `Остаток оплачен ${when(expertise.final_paid_at)}. Приложите подписанное заключение`,
          form: <ConclusionForm pending={actions.pending} onSubmit={actions.submitConclusion} />,
        };

      case "sent":
        return { text: `Заключение отправлено ${when(expertise.sent_at)}. Ждём приёмки` };

      case "accepted":
        return { text: `Работа принята ${when(expertise.accepted_at)}` };
    }
  };

  const step = role === "customer" ? customerStep() : expertStep();
  const finished = expertise.status === "accepted";
  const waiting = !step.action && !step.form && !finished;

  return (
    <div className={styles.footer}>
      <div className={styles.row}>
        <p className={`${styles.text} ${finished ? styles.textDone : ""}`}>
          {waiting && <ClockIcon className={styles.icon} />}
          {finished && <CheckIcon className={styles.icon} />}
          {step.text}
        </p>

        {step.action && <div className={styles.buttons}>{step.action}</div>}
      </div>

      {step.form}

      {role === "customer" && invoice !== null && invoice.reported_at !== null && (
        <p className={styles.note}>
          {guaranteed
            ? `Вы отправили гарантийное письмо по счёту № ${invoice.number} ${when(invoice.reported_at)}. Администратор рассмотрит его и подтвердит`
            : `Вы сообщили об оплате счёта № ${invoice.number} ${when(invoice.reported_at)}. Администратор проверит поступление на расчётный счёт и подтвердит оплату`}
        </p>
      )}

      {actions.error && <p className={styles.error}>{actions.error}</p>}
    </div>
  );
};

export default ExpertiseActions;
