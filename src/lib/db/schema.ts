import { relations } from "drizzle-orm";
import { integer, sqliteTable, text } from "drizzle-orm/sqlite-core";

export const Models = sqliteTable("models", {
    id: integer("id").primaryKey(),
    name: text("name").notNull(),
    description: text("description"),
    created_at: text("created_at").default("CURRENT_TIMESTAMP"),
});

export const Images = sqliteTable("images", {
    id: integer("id").primaryKey(),
    file_path: text("file_path").notNull(),
    uploaded_at: text("uploaded_at").default("CURRENT_TIMESTAMP"),
});

export const OCRResults = sqliteTable("ocr_results", {
    id: integer("id").primaryKey(),
    image_id: integer("image_id").references(() => Images.id),
    model_id: integer("model_id").references(() => Models.id),
    extracted_text: text("extracted_text").notNull(),
    created_at: text("created_at").default("CURRENT_TIMESTAMP"),
});

export const ModelsRelations = relations(Models, ({ many }) => ({
    ocrResults: many(OCRResults),
}));

export const ImagesRelations = relations(Images, ({ many }) => ({
    ocrResults: many(OCRResults),
}));

export const OCRResultsRelations = relations(OCRResults, ({ one }) => ({
    image: one(Images, {
        fields: [OCRResults.image_id],
        references: [Images.id],
    }),
    model: one(Models, {
        fields: [OCRResults.model_id],
        references: [Models.id],
    }),
}));
