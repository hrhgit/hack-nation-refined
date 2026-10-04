import {isMain} from '../cli.js';
import {main as lookupMain} from '../lookup/cli.js';
export const main = (argv = process.argv.slice(2)): Promise<number> => lookupMain(['changes', ...argv]);
if (isMain(import.meta.url)) main().then(code => {process.exitCode = code;}).catch(e => {console.error('第二、三阶段停止：' + e.message); process.exitCode = 1;});
