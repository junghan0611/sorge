import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { once } from 'node:events';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import worker from './worker.mjs';
import { previewServer } from './local.mjs';

const sha = 'a'.repeat(40);
const request = (query = `commit=${sha}`, method = 'GET') =>
	new Request(`https://example.test/api/snapshot?${query}`, { method });

function fixture(overrides = {}) {
	const reads = [];
	let disposed = 0;
	const repo = {
		async readCommit(commitId) { return { hash: commitId }; },
		async readFile(args) { reads.push(args); return new Blob(['hello']); },
		[Symbol.dispose]() { disposed++; },
		...overrides,
	};
	return {
		env: { REPO_NAME: 'sandbox', ARTIFACTS: { async get(name) {
			assert.equal(name, 'sandbox');
			return repo;
		} } },
		reads,
		disposed: () => disposed,
	};
}

test('page is available without a configured backend', async () => {
	const response = await worker.fetch(new Request('https://example.test/'), {});
	assert.equal(response.status, 200);
	assert.match(await response.text(), /textContent/);
});

test('all files are pinned to the supplied commit; capability is released', async () => {
	const f = fixture();
	const response = await worker.fetch(request(), f.env);
	assert.equal(response.status, 200);
	assert.equal(response.headers.get('cache-control'), 'no-store');
	assert.equal((await response.json()).commitId, sha);
	assert.deepEqual(f.reads, ['README.md', 'AGENTS.md'].map(path => ({ ref: sha, path })));
	assert.equal(f.disposed(), 1);
});

test('missing files stay null, not invented content', async () => {
	const f = fixture({ async readFile() { return null; } });
	const response = await worker.fetch(request(), f.env);
	assert.deepEqual((await response.json()).files, { 'README.md': null, 'AGENTS.md': null });
});

test('missing commit is 404 and releases the capability', async () => {
	const f = fixture({ async readCommit() { return null; } });
	assert.equal((await worker.fetch(request(), f.env)).status, 404);
	assert.equal(f.reads.length, 0);
	assert.equal(f.disposed(), 1);
});

test('branches and malformed hashes are rejected before any backend call', async () => {
	for (const commit of ['', 'main', '-x', 'a'.repeat(41), 'A'.repeat(40), '<script>']) {
		assert.equal((await worker.fetch(request(`commit=${encodeURIComponent(commit)}`), {})).status, 400);
	}
});

test('unconfigured backend is explicit', async () => {
	const response = await worker.fetch(request(), {});
	assert.equal(response.status, 503);
	assert.deepEqual(await response.json(), { error: 'not_configured' });
});

test('backend errors do not leak details and still release the capability', async () => {
	const f = fixture({ async readFile() { throw new Error('secret token'); } });
	const response = await worker.fetch(request(), f.env);
	assert.equal(response.status, 502);
	assert.doesNotMatch(await response.text(), /secret token/);
	assert.equal(f.disposed(), 1);
});

test('get failure is sanitized', async () => {
	const env = { REPO_NAME: 'sandbox', ARTIFACTS: { async get() { throw new Error('secret'); } } };
	assert.equal((await worker.fetch(request(), env)).status, 502);
});

test('write methods are unavailable', async () => {
	for (const method of ['POST', 'PUT', 'PATCH', 'DELETE']) {
		const response = await worker.fetch(request('', method), {});
		assert.equal(response.status, 405);
		assert.equal(response.headers.get('allow'), 'GET');
	}
});

test('unknown routes are 404', async () => {
	assert.equal((await worker.fetch(new Request('https://example.test/tokens'), {})).status, 404);
});

test('HTTP preview reads a real local Git commit, explicitly not Artifacts', async () => {
	const root = fileURLToPath(new URL('../../', import.meta.url));
	const commit = execFileSync('git', ['-C', root, 'rev-parse', 'HEAD'], { encoding: 'utf8' }).trim();
	const server = previewServer();
	server.listen(0, '127.0.0.1');
	await once(server, 'listening');
	try {
		const response = await fetch(`http://127.0.0.1:${server.address().port}/api/snapshot?commit=${commit}`);
		assert.equal(response.status, 200);
		const data = await response.json();
		assert.equal(data.commitId, commit);
		assert.equal(data.commit.source, 'local-git-preview');
		assert.match(data.files['README.md'], /sorge/);
	} finally {
		await new Promise((resolve, reject) => server.close(error => error ? reject(error) : resolve()));
	}
});
