# TRIAGE — 은퇴했다

```bash
./run.sh board          # 라이브 이슈판
./run.sh board --mine    # 내 몫 (cwd 로 집을 유추)
```

**이 파일엔 아무 상태도 없다.** 습관으로 열었다면 위 두 줄이 전부다.

상태는 이슈 라벨에 산다. 규약은 `LOOP.md § 상태`, 구현과 그 이유는
`.claude/skills/sorge/scripts/labels.py` 헤더. 옛 83줄은 `git log -- TRIAGE.md`.

죽은 이유 한 줄: **파일은 「적힌 게 아직 참인가」를 못 묻는다.** 커맨드는 기억하지 않아서 묻는다.
