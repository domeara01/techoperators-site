// Writes a fresh copy of the member directory data for the redesigned directory page.
//   node snapshot/snapshot-data.mjs <out snapshot.js> <fallback snapshot.js>
// Reads the directory API address from redesign/src/members.tpl.html, so there is one place to change it.
// If the live data can't be fetched, the last good copy is used so a deploy never ships an empty directory.
import { readFile, writeFile, copyFile } from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const here = path.dirname(fileURLToPath(import.meta.url));
const [,, outPath, lastPath] = process.argv;
if (!outPath || !lastPath) { console.error('Usage: node snapshot-data.mjs <out> <fallback>'); process.exit(1); }

const tpl = await readFile(path.join(here, '..', 'redesign', 'src', 'members.tpl.html'), 'utf8');
const api = (tpl.match(/https:\/\/script\.google\.com\/macros\/s\/[A-Za-z0-9_-]+\/exec/) || [])[0];
if (!api) { console.error('   Could not find the directory API address in redesign/src/members.tpl.html'); process.exit(1); }

let ok = false;
try {
  const ctl = new AbortController(); const t = setTimeout(() => ctl.abort(), 45000);
  const r = await fetch(api + '?action=directory', { redirect: 'follow', signal: ctl.signal });
  clearTimeout(t);
  const j = await r.json();
  if (j && j.members && j.members.length) {
    await writeFile(outPath, `window.__DIRECTORY_SNAPSHOT = ${JSON.stringify({ at: Date.now(), data: j })};`);
    await copyFile(outPath, lastPath);
    console.log(`   Directory snapshot: ${j.members.length} members (live)`);
    ok = true;
  } else console.log('   Live directory came back empty');
} catch (e) { console.log('   Could not fetch the live directory (' + e.message + ')'); }

if (!ok) {
  await copyFile(lastPath, outPath);
  console.log('   Using the last good copy of the directory data; the page still refreshes from the live data in the browser');
}
