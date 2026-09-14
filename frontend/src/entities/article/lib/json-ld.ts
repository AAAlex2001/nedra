import { SITE_LEGAL_NAME, SITE_URL } from "@/shared/config/seo";
import type { Article } from "../model/types";
import { articlePath } from "./paths";

const MIN_FAQ_ITEMS = 3;
const MAX_ANSWER_LENGTH = 900;

const stripTags = (html: string): string =>
  html
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/&laquo;|&raquo;/g, '"')
    .replace(/&mdash;|&ndash;/g, "—")
    .replace(/&amp;/g, "&")
    .replace(/\s+/g, " ")
    .trim();

const cutAnswer = (text: string): string => {
  if (text.length <= MAX_ANSWER_LENGTH) return text;

  const cut = text.slice(0, MAX_ANSWER_LENGTH);
  const lastDot = cut.lastIndexOf(". ");

  if (lastDot > MAX_ANSWER_LENGTH / 2) return cut.slice(0, lastDot + 1);

  return `${cut.trimEnd()}…`;
};

const sectionText = (content: string, anchor: string, nextAnchor: string | null): string => {
  const start = content.indexOf(`<h2 id="${anchor}"`);
  if (start === -1) return "";

  const afterHeading = content.indexOf("</h2>", start);
  if (afterHeading === -1) return "";

  let end = content.length;
  if (nextAnchor) {
    const nextStart = content.indexOf(`<h2 id="${nextAnchor}"`);
    if (nextStart > afterHeading) end = nextStart;
  }

  return stripTags(content.slice(afterHeading + "</h2>".length, end));
};

export const buildArticleJsonLd = (article: Article) => ({
  "@context": "https://schema.org",
  "@type": "Article",
  headline: article.title,
  description: article.description ?? undefined,
  image: article.cover_image ? `${SITE_URL}${article.cover_image}` : undefined,
  datePublished: article.published_at ?? undefined,
  dateModified: article.updated_at ?? article.published_at ?? undefined,
  inLanguage: "ru-RU",
  author: { "@type": "Organization", name: SITE_LEGAL_NAME, url: SITE_URL },
  publisher: {
    "@type": "Organization",
    name: SITE_LEGAL_NAME,
    logo: { "@type": "ImageObject", url: `${SITE_URL}/logo.svg` },
  },
  mainEntityOfPage: `${SITE_URL}${articlePath(article)}`,
});

export const buildFaqJsonLd = (article: Article) => {
  const questions = article.toc.filter((item) => item.title.trim().endsWith("?"));

  if (questions.length < MIN_FAQ_ITEMS) return null;

  const items = questions.map((item) => {
    const position = article.toc.findIndex((entry) => entry.id === item.id);
    const next = article.toc[position + 1];
    const answer = sectionText(article.content, item.id, next ? next.id : null);

    return { question: item.title, answer };
  });

  const filled = items.filter((item) => item.answer.length > 80);

  if (filled.length < MIN_FAQ_ITEMS) return null;

  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: filled.map((item) => ({
      "@type": "Question",
      name: item.question,
      acceptedAnswer: { "@type": "Answer", text: cutAnswer(item.answer) },
    })),
  };
};
