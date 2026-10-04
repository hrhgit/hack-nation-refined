import {spawnSync} from 'node:child_process';
const parity = process.argv.includes('--typescript');
const args = ['-m', 'unittest', 'discover', '-s', 'tests'];
if (parity) args.push('-p', 'test_migration_*.py');
args.push('-v');
const result = spawnSync(process.env.PYTHON ?? 'python3', args, {stdio: 'inherit', env: {...process.env, MIGRATION_BACKEND: parity ? 'typescript' : 'python'}});
if (result.error) {console.error(result.error.message); process.exitCode = 1;}
else process.exitCode = result.status ?? 1;
