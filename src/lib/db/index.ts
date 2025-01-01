import { drizzle, type AsyncRemoteCallback } from "drizzle-orm/sqlite-proxy";
import Database from "@tauri-apps/plugin-sql";
import * as schema from "./schema";

/**
 * Represents the result of a SELECT query.
 */
export type SelectQueryResult<T extends Record<string, unknown>> = {
    [K in keyof T]: T[K];
};
/**
 * Loads the sqlite database via the Tauri Proxy.
 */
let sqlite: Database | null = null;
export async function initSqlite() {
    if (!sqlite) {
        sqlite = await Database.load("sqlite:sqlite.db");
    }
    return sqlite;
}

const asyncRemoteCallback: AsyncRemoteCallback = async (sql, params, method) => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    let rows: any[] = [];
    let results = [];

    if (!sqlite) {
        await initSqlite();
    }

    // If the query is a SELECT, use the select method
    if (isSelectQuery(sql)) {
        rows = await sqlite!.select(sql, params).catch((e) => {
            console.error("SQL Error:", e);
            return [];
        }) as any[]; // eslint-disable-line @typescript-eslint/no-explicit-any
    } else {
        // Otherwise, use the execute method
        await sqlite!.execute(sql, params).catch((e) => {
            console.error("SQL Error:", e);
            return [];
        });
        return { rows: [] };
    }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    rows = rows.map((row: any) => {
        return Object.values(row);
    });

    // If the method is "all", return all rows
    results = method === "all" ? rows : rows[0];

    return { rows: results };
}


/**
 * The drizzle database instance.
 */
export const db = drizzle<typeof schema>(
    asyncRemoteCallback,
    // Pass the schema to the drizzle instance
    { schema: schema, logger: true }
);

/**
 * Checks if the given SQL query is a SELECT query.
 * @param sql The SQL query to check.
 * @returns True if the query is a SELECT query, false otherwise.
 */
function isSelectQuery(sql: string): boolean {
    const selectRegex = /^\s*SELECT\b/i;
    return selectRegex.test(sql);
}