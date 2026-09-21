import type { Article } from "../model/types";

export const splitContent = (article: Article): [string, string] => {
  if (article.toc.length < 2) return [article.content, ""];

  const middle = article.toc[Math.floor(article.toc.length / 2)];
  const marker = `<h2 id="${middle.id}"`;
  const index = article.content.indexOf(marker);

  if (index <= 0) return [article.content, ""];

  return [article.content.slice(0, index), article.content.slice(index)];
};

export const splitBeforeFirstHeading = (content: string): [string, string] => {
  const index = content.indexOf("<h2");

  if (index <= 0) return [content, ""];

  return [content.slice(0, index), content.slice(index)];
};
