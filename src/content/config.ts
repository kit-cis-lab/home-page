import { file } from "astro/loaders";
import { defineCollection, z } from "astro:content";

const newsCollection = defineCollection({
  type: "content",
  schema: z.object({
    date: z.date(),
  }),
});

const achievementsCollection = defineCollection({
  // loader: file("src/content/achievements/data.json", {
  loader: file("src/content/achievements/data copy.json", {
    parser: (text) => {
      const obj = JSON.parse(text);
      return Object.fromEntries(
        Object.entries(obj).map(([key, value]) => {
          const val = value as Record<string, any>;
          return [key, { ...val, date: new Date(val.date) }];
        }),
      );
    },
  }),
  schema: z.object({
    date: z.date(),
    title: z.string(),
    tags: z.array(z.string()),
    authors: z.array(z.string()),
    year: z.string(),
    publisher: z.string(),
    link: z.string().url().optional(),
  }),
});

export const collections = {
  news: newsCollection,
  achievements: achievementsCollection,
};
