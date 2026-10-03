#!/usr/bin/env bash
# gate_topic 시험 세트(집행 완료 조건) — 반려 15/15 실패 · 라이브 22/22 실패 · 달력 20 통과 수(16) · 분야 예시 · 시연 통과 · 영문 경계·B7 소문자·별명·오탐 · 공격형(낸 키·넓은 날짜·꼬리 붙이기) · 레포 쪽(진행분·반려_추가·회장 예외) · fail-closed(빈 입력·깨진 데이터·--repo)
# 사용: bash 시험/run_tests_topic.sh [서치 레포 루트]   (레포를 주면 실제 레포로도 한 번 돌려 기록한다)
# 종료: 0 = 모두 기대대로 · 1 = 다른 것 있음
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="${1:-}"
if [ -n "$REPO" ]; then
  exec python3 "$HERE/topic_test.py" --repo "$REPO"
else
  exec python3 "$HERE/topic_test.py"
fi
