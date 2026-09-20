type ValidationItem = {
  msg?: string;
};

export const readErrorMessage = async (response: Response): Promise<string> => {
  try {
    const body = await response.json();

    if (typeof body.detail === "string") return body.detail;

    if (Array.isArray(body.detail)) {
      const messages = body.detail
        .map((item: ValidationItem) => item.msg ?? "")
        .filter((message: string) => message !== "");

      if (messages.length > 0) return messages.join(". ");
    }
  } catch {
    return `Ошибка ${response.status}`;
  }

  return `Ошибка ${response.status}`;
};
