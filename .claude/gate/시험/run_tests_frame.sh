#!/usr/bin/env bash
# gate_frame · overlap21 · gate_search 시험 세트.
# 사용: bash run_tests_frame.sh [서치 레포 루트] [라이브 스냅숏 폴더]
#   레포를 안 주면: 이 파일이 <레포>/.claude/gate/시험/ 안에 있으면 그 레포, 아니면 환경변수 SEARCH_REPO.
#   스냅숏을 안 주면: 환경변수 LIVE_DIR. 없으면 라이브 대조 시험은 「건너뜀」(실패 아님). 스냅숏은 커밋하지 않는다.
# 종료코드: 기대와 다른 시험이 하나라도 있으면 1.
DIR="$(cd "$(dirname "$0")" && pwd)"
ARGS=()
[ -n "$1" ] && ARGS+=(--repo "$1")
[ -n "$2" ] && ARGS+=(--live "$2")
exec python3 "$DIR/run_tests_frame.py" "${ARGS[@]}"
