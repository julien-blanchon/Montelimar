import { defineConfig, type Config } from 'drizzle-kit';
const isDevMode = process.env.NODE_ENV === 'development';

export default defineConfig({
    dialect: 'sqlite',
    schema: './src/lib/db/schema.ts',
    out: './src-tauri/migrations',
    dbCredentials: {
        url: isDevMode ?
            '/Users/julienblanchon/Library/Application Support/com.montelimar.app/' + 'sqlite.db' :
            ':memory:'
    },
    verbose: true,
    strict: true
}) satisfies Config;