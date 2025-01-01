import { initSqlite } from './index'
import { readDir, readFile, type DirEntry } from '@tauri-apps/plugin-fs';
import { resourceDir } from '@tauri-apps/api/path';

export type ProxyMigrator = (migrationQueries: string[]) => Promise<void>

export async function migrate() {
    const resourcePath = await resourceDir();
    const files = await readDir(`${resourcePath}/migrations`);
    let migrations = files.filter((file) => file.name?.endsWith('.sql'));

    migrations = migrations.sort((a: DirEntry, b: DirEntry) => {
        const aHash = a.name?.slice(0, 4)
        const bHash = b.name?.slice(0, 4)

        if (aHash && bHash) {
            return aHash.localeCompare(bHash)
        }

        return 0
    })

    const migrationTableCreate = /* sql */ `
    CREATE TABLE IF NOT EXISTS "__drizzle_migrations" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hash text NOT NULL UNIQUE,
      created_at numeric
    )
  `
    const sqlite = await initSqlite();

    await sqlite.execute(migrationTableCreate, [])

    for (const hash of migrations) {
        const dbMigrations = (await sqlite.select(
      /* sql */ `SELECT id, hash, created_at FROM "__drizzle_migrations" ORDER BY created_at DESC`,
        )) as unknown as { id: number, hash: string, created_at: number }[]

        const hasBeenRun = (hash: string) =>
            dbMigrations.find((dbMigration) => {
                return dbMigration?.hash === hash
            })

        if (hash && hasBeenRun(hash.name) === undefined) {
            // Lese die Datei als Uint8Array
            const fileData: Uint8Array = await readFile(`${resourcePath}/migrations/${hash.name}`);

            // Konvertiere den ArrayBuffer zu einem String
            const sql = arrayBufferToString(fileData.buffer as ArrayBuffer);

            if (sql) {
                sqlite.execute(sql, [])
                sqlite.execute(
        /* sql */ `INSERT INTO "__drizzle_migrations" (hash, created_at) VALUES ($1, $2)`,
                    [hash, Date.now()],
                )
            }
        }
    }

    return Promise.resolve()
}

function arrayBufferToString(buffer: ArrayBuffer): string {
    const decoder = new TextDecoder('utf-8');
    return decoder.decode(buffer);
}