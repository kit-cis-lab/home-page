import { defineCollection, z } from 'astro:content';

const newsCollection = defineCollection({
  type: 'content',
  schema: z.object({
    date: z.date(),
  }),
});

export const collections = {
  news: newsCollection,
};
