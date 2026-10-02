#!/usr/bin/env bash
# 감찰 미실행 경고 (D-047)
# 작업 폴더가 원고 단계까지 갔는데 감찰 보고가 하나도 없으면 경고한다.
# 감찰은 「진행」이 지점 A/B/C에서 부른다. 사장도 코디도 부르지 않는다.
set -uo pipefail

ROOT="${CLAUDE_PROJECT_DIR:-}"
[ -n "$ROOT" ] || ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT" 2>/dev/null || exit 0
[ -d "작업" ] || exit 0

missing=()
for d in 작업/*/; do
  [ -d "$d" ] || continue
  key="$(basename "$d")"
  # 원고까지 간 폴더만 본다 (그 전에는 감찰 지점 A/B가 아직 안 왔을 수 있다)
  [ -f "$d/05_원고.md" ] || continue
  if ! ls 운영/감찰보고/*"$key"* >/dev/null 2>&1; then
    missing+=("$key")
  fi
done

[ ${#missing[@]} -eq 0 ] && exit 0

list="$(printf '%s, ' "${missing[@]}")"; list="${list%, }"
msg="⚠ 감찰 미실행: ${list} — 원고까지 갔는데 운영/감찰보고/ 에 보고가 없습니다. 감찰은 「진행」이 부릅니다(D-047). 사장도 코디도 부르지 않습니다."
printf '{"systemMessage":%s}\n' "$(printf '%s' "$msg" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')"
exit 0
