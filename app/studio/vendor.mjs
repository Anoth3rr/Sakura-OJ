import {copyFile, cp, mkdir, readFile, writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=path.dirname(fileURLToPath(import.meta.url));
const dest=path.join(root,'static/vendor');
await mkdir(dest,{recursive:true});
for(const [src,name] of [
  ['marked/lib/marked.umd.js','marked.umd.js'],
  ['dompurify/dist/purify.min.js','purify.min.js'],
  ['katex/dist/katex.min.js','katex.min.js'],
  ['katex/dist/katex.min.css','katex.min.css'],
  ['katex/dist/contrib/auto-render.min.js','auto-render.min.js'],
  ['marked/LICENSE','LICENSE-marked'],['dompurify/LICENSE','LICENSE-dompurify'],['katex/LICENSE','LICENSE-katex'],
])await copyFile(path.join(root,'node_modules',src),path.join(dest,name));
await cp(path.join(root,'node_modules/katex/dist/fonts'),path.join(dest,'fonts'),{recursive:true});
const manifest={};
for(const name of ['marked','dompurify','katex'])manifest[name]=JSON.parse(await readFile(path.join(root,'node_modules',name,'package.json'))).version;
await writeFile(path.join(dest,'versions.json'),JSON.stringify(manifest,null,2)+'\n');
console.log('Vendored',manifest);
