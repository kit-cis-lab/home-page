import { defineCollection, z } from "astro:content";

const newsCollection = defineCollection({
  type: "content",
  schema: z.object({
    date: z.date(),
  }),
});

const achievementsCollection = defineCollection({
  type: "content",
  schema: z.object({
    date: z.date(),
    title: z.string(),
    tags: z.array(z.string()),
    authors: z.array(z.string()),
    year: z.string(),
    publisher: z.string(),
  }),
});

export const collections = {
  news: newsCollection,
  achievements: achievementsCollection,
};
