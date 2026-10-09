import { negotiable, type Expertise } from "@/entities/expertise";
import { formatRub } from "@/shared/lib/money";
import Button from "@/shared/ui/button";
import type { ExpertiseActionsState } from "../../model/use-expertise-actions";
import AuditUpload from "../audit-upload";
import OfferAnswer from "../offer-answer";
import PlanForm from "../plan-form";
import PlanReview from "../plan-review";
import PriceForm from "../price-form";
import TeamPicker from "../team-picker";
import { when, type Step } from "./step";
import styles from "./style.module.scss";

const latestPlan = (expertise: Expertise) => {
  const plans = expertise.documents.filter((item) => item.kind === "audit_plan");

  return plans.length > 0 ? plans[plans.length - 1] : null;
};

const correction = (expertise: Expertise): string =>
  expertise.plan_comment ? `. Корректировки заказчика: «${expertise.plan_comment}»` : "";

export const auditCustomerStep = (
  expertise: Expertise,
  actions: ExpertiseActionsState,
): Step | null => {
  const open = negotiable(expertise.audit_details);

  switch (expertise.status) {
    case "consultation":
      return {
        text: "Заявка у менеджера НПИ «Недра»: он свяжется с вами, чтобы определить тип аудита",
      };

    case "new":
      return {
        text:
          expertise.price === null
            ? "Аудиторы изучают заявку: руководитель группы предложит цену"
            : "Ждём, когда аудитор возьмёт заявку",
      };

    case "offer":
      return {
        text: `Аудитор НПИ «Недра» изучил заявку и предлагает провести аудит за ${formatRub(expertise.offer_price)}`,
        form: (
          <OfferAnswer
            offer={Number(expertise.offer_price)}
            negotiable={open}
            pending={actions.pending}
            onAnswer={(answer, price) => void actions.answerOffer(answer, price)}
          />
        ),
      };

    case "counter":
      return {
        text: `Вы предложили ${formatRub(expertise.counter_price)}. Ждём ответа аудитора`,
      };

    case "plan":
      return {
        text: `Аванс оплачен ${when(expertise.advance_paid_at)}. Руководитель аудиторской группы готовит План аудита${correction(expertise)}`,
      };

    case "plan_review":
      return {
        text: "План аудита ждёт вашего согласования: проверьте состав группы, график и запрашиваемые ресурсы",
        form: (
          <PlanReview
            expertiseId={expertise.id}
            plan={latestPlan(expertise)}
            pending={actions.pending}
            onApprove={() => void actions.approvePlan()}
            onRequestChanges={(comment) => void actions.requestPlanChanges(comment)}
          />
        ),
      };

    case "in_progress":
      return {
        text: `План согласован ${when(expertise.plan_approved_at)}. Загрузите документы по перечню — аудиторская группа проверяет их`,
        form: <AuditUpload pending={actions.pending} onUpload={actions.uploadDocuments} />,
      };

    default:
      return null;
  }
};

const newAuditStep = (expertise: Expertise, actions: ExpertiseActionsState): Step => {
  const open = negotiable(expertise.audit_details);
  const offerForm = (
    <PriceForm
      label="Ваша цена, ₽"
      submitText="Предложить цену заказчику"
      pending={actions.pending}
      onSubmit={(price) => void actions.proposePrice(price)}
    />
  );

  if (expertise.price === null) {
    return {
      text: "Заказчик не установил бюджет. Изучите заявку и предложите цену — не ниже 100 000 ₽",
      form: offerForm,
    };
  }

  return {
    text: open
      ? `Заказчик предлагает ${formatRub(expertise.price)} и готов обсуждать стоимость. Возьмите заявку по этой цене или предложите свою`
      : `Заказчик предлагает ${formatRub(expertise.price)}, бюджет фиксирован. Нажимая «Готов провести», вы соглашаетесь с ценой`,
    action: (
      <Button loading={actions.pending} onClick={() => void actions.accept(null)}>
        Готов провести аудит
      </Button>
    ),
    form: open ? offerForm : null,
  };
};

export const auditExpertStep = (
  expertise: Expertise,
  actions: ExpertiseActionsState,
  lead: boolean,
): Step | null => {
  if (expertise.status === "new") return newAuditStep(expertise, actions);

  if (!lead) {
    return { text: "Вы в аудиторской группе. Заявку ведёт руководитель группы" };
  }

  switch (expertise.status) {
    case "offer":
      return {
        text: `Вы предложили ${formatRub(expertise.offer_price)}. Ждём ответа заказчика`,
      };

    case "counter":
      return {
        text: `Заказчик предлагает ${formatRub(expertise.counter_price)} вместо ${formatRub(expertise.offer_price)}`,
        action: (
          <>
            <button
              type="button"
              className={styles.secondary}
              disabled={actions.pending}
              onClick={() => void actions.answerCounter(false)}
            >
              Отказаться
            </button>
            <Button loading={actions.pending} onClick={() => void actions.answerCounter(true)}>
              Принять {formatRub(expertise.counter_price)}
            </Button>
          </>
        ),
      };

    case "contract":
      return {
        text: `Договор заключён ${when(expertise.contract_at)}. Ждём аванс. Пока можно сформировать аудиторскую группу`,
        form: (
          <TeamPicker
            team={expertise.team}
            pending={actions.pending}
            onSave={(userIds) => void actions.saveTeam(userIds)}
          />
        ),
      };

    case "plan":
      return {
        text: `Аванс оплачен ${when(expertise.advance_paid_at)}. Сформируйте группу и отправьте заказчику План аудита${correction(expertise)}`,
        form: (
          <>
            <TeamPicker
              team={expertise.team}
              pending={actions.pending}
              onSave={(userIds) => void actions.saveTeam(userIds)}
            />
            <PlanForm
              expertise={expertise}
              pending={actions.pending}
              onSubmit={(plan) => void actions.sendPlan(plan)}
            />
          </>
        ),
      };

    case "plan_review":
      return {
        text: `План отправлен ${when(expertise.plan_sent_at)}. Ждём согласования заказчика`,
      };

    default:
      return null;
  }
};
