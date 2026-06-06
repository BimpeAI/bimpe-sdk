// Stamp src/version.ts from package.json so the version baked into the bundle
// (and the User-Agent header) always matches the published package version.
// Runs as part of `build`, after changesets has bumped package.json.
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const { version } = JSON.parse(readFileSync(join(here, '..', 'package.json'), 'utf8'));
const target = join(here, '..', 'src', 'version.ts');
const contents = `export const VERSION = '${version}';\n`;

const current = (() => {
  try {
    return readFileSync(target, 'utf8');
  } catch {
    return '';
  }
})();

if (current !== contents) {
  writeFileSync(target, contents);
}
console.log(`version: src/version.ts stamped to ${version}`);
