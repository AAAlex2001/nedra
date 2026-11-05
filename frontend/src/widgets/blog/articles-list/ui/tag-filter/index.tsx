import type { PublishedArticleSort, Tag } from "@/entities/article";
import { buildListHref } from "../../lib/list-href";
import ListFilter from "../list-filter";

type TagFilterProps = {
  basePath: string;
  tags: Tag[];
  activeTag: string | null;
  search: string;
  sort: PublishedArticleSort;
};

const TagFilter = ({ basePath, tags, activeTag, search, sort }: TagFilterProps) => {
  const options = [
    {
      value: "",
      label: "Все направления",
      href: buildListHref(basePath, { tag: null, search, sort }),
    },
    ...tags.map((tag) => ({
      value: tag.slug,
      label: tag.title,
      href: buildListHref(basePath, { tag: tag.slug, search, sort }),
    })),
  ];

  return (
    <ListFilter
      label="Направление"
      options={options}
      value={activeTag ?? ""}
      highlighted={Boolean(activeTag)}
    />
  );
};

export default TagFilter;
