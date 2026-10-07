"use client";

import { useEffect, useReducer } from "react";
import { fetchMyExpertises, type CustomerType } from "@/entities/expertise";
import { INITIAL_STATE, orderReducer } from "./reducer";
import type { CompanyField, Deadline, IndividualField } from "./types";

type OrderRequest = (formData: FormData) => Promise<unknown>;

const SUBMIT_FAILED = "Не удалось отправить заявку. Попробуйте ещё раз.";

const OPTIONAL_COMPANY_FIELDS: CompanyField[] = ["kpp"];

const parsePrice = (value: string): number => Number(value.replace(/\s/g, "").replace(",", "."));

const allFilled = (fields: Record<string, string>, optional: string[] = []): boolean =>
  Object.entries(fields).every(([field, value]) => optional.includes(field) || value.trim() !== "");

export const useOrder = () => {
  const [state, dispatch] = useReducer(orderReducer, INITIAL_STATE);

  useEffect(() => {
    const fillFromLastOrder = async () => {
      try {
        const items = await fetchMyExpertises();
        const lastCompany = items.find((item) => item.company !== null)?.company;
        const lastIndividual = items.find((item) => item.individual !== null)?.individual;

        if (lastCompany) dispatch({ type: "company/fill", company: lastCompany });
        if (lastIndividual) dispatch({ type: "individual/fill", individual: lastIndividual });
        if (items[0]) dispatch({ type: "customer/select", customerType: items[0].customer_type });
      } catch {
        return;
      }
    };

    void fillFromLastOrder();
  }, []);

  const price = parsePrice(state.price);
  const legal = state.customerType === "legal";
  const customerFilled = legal
    ? allFilled(state.company, OPTIONAL_COMPANY_FIELDS)
    : allFilled(state.individual);

  const ready =
    state.objectName.trim() !== "" && price > 0 && customerFilled && state.status !== "loading";

  const payload = {
    object_name: state.objectName.trim(),
    price,
    customer_type: state.customerType,
    company: legal ? { ...state.company, kpp: state.company.kpp.trim() || null } : null,
    individual: legal ? null : state.individual,
    deadline: state.deadline,
    comment: state.comment.trim() || null,
  };

  const changeObjectName = (value: string) => dispatch({ type: "objectName/change", value });
  const selectDeadline = (value: Deadline) => dispatch({ type: "deadline/select", value });
  const changePrice = (value: string) => dispatch({ type: "price/change", value });
  const selectCustomerType = (customerType: CustomerType) =>
    dispatch({ type: "customer/select", customerType });
  const changeCompany = (field: CompanyField, value: string) =>
    dispatch({ type: "company/change", field, value });
  const changeIndividual = (field: IndividualField, value: string) =>
    dispatch({ type: "individual/change", field, value });
  const removeCard = () => dispatch({ type: "card/remove" });
  const changeComment = (value: string) => dispatch({ type: "comment/change", value });
  const closeSuccess = () => dispatch({ type: "success/close" });

  const setCard = (files: File[]) => {
    const [file] = files;
    if (file) dispatch({ type: "card/set", file });
  };

  const send = async (formData: FormData, request: OrderRequest) => {
    dispatch({ type: "submit/start" });

    if (legal && state.companyCard) {
      formData.append("company_card", state.companyCard);
    }

    try {
      await request(formData);
      dispatch({ type: "submit/success" });
    } catch (error) {
      const message = error instanceof Error && error.message ? error.message : SUBMIT_FAILED;
      dispatch({ type: "submit/error", message });
    }
  };

  return {
    state,
    dispatch,
    ready,
    payload,
    changeObjectName,
    selectDeadline,
    changePrice,
    selectCustomerType,
    changeCompany,
    changeIndividual,
    setCard,
    removeCard,
    changeComment,
    closeSuccess,
    send,
  };
};

export type Order = ReturnType<typeof useOrder>;
