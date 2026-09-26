#!/usr/bin/env bash
# 정체 감지 (D-056 · 회장 승인 2026-09-22)
# 열린 작업 폴더의 공정일지에 N턴 연속 새 줄이 없으면 경고한다.
#
# D-048 훅(check-gamchal.sh)은 05_원고.md가 생긴 뒤에만 운다.
# 「진행」을 아예 안 띄우면 원고가 영영 안 생기므로 그 훅은 영원히 안 운다.
# 이 훅이 그 구멍을 막는다 — 공정이 멈춘 것 자체를 본다.
set -uo pipefail

THRESHOLD=3

ROOT="${CLAUDE_PROJECT_DIR:-}"
[ -n "$ROOT" ] || ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT" 2>/dev/null || exit 0
[ -d "작업" ] || exit 0

STATE="$ROOT/.claude/hooks/.stall-state"
touch "$STATE" 2>/dev/null || exit 0

stalled=()
new_state=""

for d in 작업/*/; do
  [ -d "$d" ] || continue
  log="$d/00_공정일지.md"
  [ -f "$log" ] || continue
  key="$(basename "$d")"

  # 닫힌 폴더는 안 본다. 공정일지에 [발행] 또는 [종료]가 찍히면 닫힌 것으로 본다.
  if grep -qE '^\[(발행|종료)\]' "$log" 2>/dev/null; then
    continue
  fi

  # 손 뗀 폴더도 안 본다. 정체는 「돌던 것이 섰다」이지 「끝난 것이 조용하다」가 아니다.
  # 공정일지를 24시간 넘게 안 건드렸으면 도는 폴더가 아니다.
  if [ -n "$(find "$log" -mmin +1440 -print 2>/dev/null)" ]; then
    continue
  fi

  size="$(wc -c < "$log" | tr -d ' ')"
  prev="$(awk -F'\t' -v k="$key" '$1==k {print $2"\t"$3}' "$STATE" 2>/dev/null | head -1)"
  prev_size="${prev%%	*}"
  prev_count="${prev##*	}"
  [ -n "$prev_size" ] || prev_size=""
  case "$prev_count" in ''|*[!0-9]*) prev_count=0 ;; esac

  if [ "$size" = "$prev_size" ]; then
    count=$((prev_count + 1))
  else
    count=0
  fi

  new_state="${new_state}${key}	${size}	${count}
"
  [ "$count" -ge "$THRESHOLD" ] && stalled+=("${key}(${count}턴)")
done

printf '%s' "$new_state" > "$STATE" 2>/dev/null

[ ${#stalled[@]} -eq 0 ] && exit 0

list="$(printf '%s, ' "${stalled[@]}")"; list="${list%, }"
msg="⚠ 공정 정체: ${list} — 공정일지에 새 줄이 없습니다. 「진행」이 끊겼는지 디스크로 확인하고, 끊겼으면 띄운 손이 다시 띄웁니다(D-056 ③). 재기동하는 손은 도달 지점을 먼저 확인하고 지나간 감찰 지점부터 돌립니다."
printf '{"systemMessage":%s}\n' "$(printf '%s' "$msg" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')"
exit 0
