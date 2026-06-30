import { readdir, readFile } from "node:fs/promises";
import { join } from "node:path";

const forbidden = ["CONTEXTOS_SUPABASE_SECRET_KEY", "SUPABASE_SECRET_KEY", "service_role"];
const roots = ["app", "components", "features", "lib", "public", ".next/static"];

async function files(root) {
  try {
    const entries = await readdir(root, { withFileTypes: true });
    const nested = await Promise.all(
      entries.map((entry) => {
        const path = join(root, entry.name);
        return entry.isDirectory() ? files(path) : [path];
      }),
    );
    return nested.flat();
  } catch {
    return [];
  }
}

const allFiles = (await Promise.all(roots.map(files))).flat();
for (const file of allFiles) {
  const text = await readFile(file, "utf8").catch(() => "");
  for (const token of forbidden) {
    if (text.includes(token)) {
      console.error(`Forbidden frontend secret marker found in ${file}`);
      process.exit(1);
    }
  }
}
