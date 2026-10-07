// Local preview only. This adapter reads Git; it does not exercise Artifacts.
import { execFile } from 'node:child_process';
import { createServer } from 'node:http';
import { promisify } from 'node:util';
import { fileURLToPath, pathToFileURL } from 'node:url';
import worker from './worker.mjs';

const exec = promisify(execFile);
const root = fileURLToPath(new URL('../../', import.meta.url));

export function localEnv(directory = root) {
	const git = async (...args) => (await exec('git', ['-C', directory, ...args], {
		maxBuffer: 1024 * 1024,
	})).stdout;
	return {
		REPO_NAME: 'local-preview (not Cloudflare)',
		ARTIFACTS: {
			async get() {
				return {
					async readCommit(hash) {
						try {
							if ((await git('cat-file', '-t', hash)).trim() !== 'commit') return null;
							return { hash, source: 'local-git-preview' };
						} catch (error) {
							if (error.code === 128) return null;
							throw error;
						}
					},
					async readFile({ ref, path }) {
						try {
							return new Blob([await git('show', `${ref}:${path}`)]);
						} catch (error) {
							if (error.code === 128) return null;
							throw error;
						}
					},
					[Symbol.dispose]() {},
				};
			},
		},
	};
}

export function previewServer(env = localEnv()) {
	return createServer(async (request, response) => {
		try {
			const result = await worker.fetch(new Request(new URL(request.url, 'http://localhost'), {
				method: request.method,
			}), env);
			response.writeHead(result.status, Object.fromEntries(result.headers));
			response.end(await result.text());
		} catch {
			response.writeHead(500);
			response.end('Local preview failed');
		}
	});
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
	previewServer().listen(8787, '127.0.0.1', () => {
		console.log('LOCAL GIT PREVIEW — NOT ARTIFACTS: http://127.0.0.1:8787');
		console.log('Paste a commit SHA from: git rev-parse HEAD');
	});
}
