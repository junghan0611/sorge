const page = `<!doctype html>
<html lang="ko">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>sorge · 코드의 한 시점</title>
<style>
body { max-width: 58rem; margin: 3rem auto; padding: 0 1rem; font-family: system-ui; }
input, button { font: inherit; padding: .5rem; }
pre { white-space: pre-wrap; overflow-wrap: anywhere; background: #eee; padding: 1rem; }
</style>
<h1>코드의 한 시점</h1>
<p>같은 출발점을 읽는 첫 실험. 변경·검토·선택 기능은 아직 없습니다.</p>
<form><label>commit <input name="commit" placeholder="40자리 Git SHA" required pattern="[0-9a-f]{40}" size="42"></label> <button>읽기</button></form>
<p id="status" role="status"></p><pre id="snapshot"></pre>
<script type="module">
const form = document.querySelector('form');
let requestNumber = 0;
form.addEventListener('submit', async (event) => {
	event.preventDefault();
	const current = ++requestNumber;
	document.querySelector('#status').textContent = '읽는 중…';
	document.querySelector('#snapshot').textContent = '';
	try {
		const response = await fetch('/api/snapshot?' + new URLSearchParams(new FormData(form)));
		const data = await response.json();
		if (current !== requestNumber) return;
		document.querySelector('#status').textContent = response.ok ? '읽음 — 쓰기 없음' : '읽지 못함';
		document.querySelector('#snapshot').textContent = JSON.stringify(data, null, 2);
	} catch {
		if (current === requestNumber) document.querySelector('#status').textContent = '연결 실패';
	}
});
const initial = new URL(location.href).searchParams.get('commit');
if (initial && /^[0-9a-f]{40}$/.test(initial)) {
	form.elements.commit.value = initial;
	form.requestSubmit();
}
</script>
</html>`;

function json(body, status = 200) {
	return Response.json(body, { status, headers: { 'cache-control': 'no-store' } });
}

export default {
	async fetch(request, env) {
		const url = new URL(request.url);
		if (request.method !== 'GET') {
			return new Response('Read-only experiment', { status: 405, headers: { allow: 'GET' } });
		}
		if (url.pathname === '/') {
			return new Response(page, { headers: {
				'content-type': 'text/html; charset=utf-8',
				'cache-control': 'no-store',
				'x-content-type-options': 'nosniff',
			} });
		}
		if (url.pathname !== '/api/snapshot') return json({ error: 'not_found' }, 404);
		const commitId = url.searchParams.get('commit') ?? '';
		if (!/^[0-9a-f]{40}$/.test(commitId)) return json({ error: 'commit_sha_required' }, 400);
		if (!env.ARTIFACTS || !env.REPO_NAME) return json({ error: 'not_configured' }, 503);
		let repo;
		try {
			repo = await env.ARTIFACTS.get(env.REPO_NAME);
			const commit = await repo.readCommit(commitId);
			if (commit === null) return json({ error: 'commit_not_found', commitId }, 404);
			// Pin every read to the same SHA; a moving branch is not a shared baseline.
			const files = {};
			for (const path of ['README.md', 'AGENTS.md']) {
				const blob = await repo.readFile({ ref: commitId, path });
				files[path] = blob === null ? null : await blob.text();
			}
			return json({ repo: env.REPO_NAME, commitId, commit, files });
		} catch {
			// Do not echo upstream errors, account details, or credentials to callers.
			return json({ error: 'artifacts_read_failed' }, 502);
		} finally {
			repo?.[Symbol.dispose]();
		}
	},
};
