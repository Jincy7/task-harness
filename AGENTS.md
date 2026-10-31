# Task Harness 룰북 지도

## 문서 작성

[README](README.md)를 사용법과 실행 안내의 원본으로 유지합니다. 스킬의 행동 규칙은 각 `SKILL.md`, 조건별 상세 지침은 해당 `references/`에 둡니다. 같은 규칙을 여러 문서에 복제하지 않습니다.

- 문서 종류와 기록 위치: [문서 작성 지침](plugins/task-harness/skills/task-docs/SKILL.md)
- 요구, 계획과 결정 기록의 형식: [문서 템플릿](plugins/task-harness/skills/task-docs/references/document-templates.md)
- 구현 전 로그 준비: [로컬 실행 기록 지침](plugins/task-harness/skills/task-build/references/runtime-logging.md)
- 그림의 작성과 검증: [다이어그램 지침](plugins/task-harness/skills/task-docs/references/diagrams.md)
- 대상 저장소의 룰북 지도 작성: [AGENTS 템플릿](plugins/task-harness/skills/task-agents/references/agents-template.md)

현재 작업에 필요한 문서만 작성합니다. 실행 방법은 README에, 플랜에는 작업 체크리스트와 보고서 링크만 둡니다. 실제 결과와 이상 상황의 원인 및 조치는 별도 작업 보고에 기록합니다. 이 지도에는 구현 현황, 테스트 결과와 환경 상태를 복제하지 않습니다. 기존 사용자 규칙과 경로를 보존하고, 실제 관측과 미확인을 구분합니다.

## 쓰기 작업의 완료 조건

Git 저장소의 쓰기 작업에는 스킬 호출 여부와 관계없이 이 조건을 적용합니다.
사용자 동작 하나나 수정 목적 하나를 구현하고 관련 검증을 통과하면 현재 작업의 diff를 확인합니다.
현재 작업의 구현, 필요한 테스트와 문서만 stage하고 staged diff를 확인한 뒤 로컬 커밋합니다.
다음 작업으로 넘어가기 전에 브랜치, 커밋 SHA와 검증 결과를 보고합니다.
커밋이 막히면 실패 이유와 미커밋 변경을 보고하며, 커밋한 것처럼 완료 처리하지 않습니다.
사용자의 커밋 보류 또는 금지 지시를 따르고 기존 사용자 변경을 임의로 포함하거나 되돌리지 않습니다.
Git이 없으면 이 조건만을 이유로 저장소를 만들지 않습니다. 원격 push와 배포는 별도 승인 범위를 따릅니다.

## 스킬 선택

| 작업 | 읽을 지침 |
| --- | --- |
| 요구 정리와 작업 분해 | [task-scope](plugins/task-harness/skills/task-scope/SKILL.md) |
| 확정된 흐름 구현 | [task-build](plugins/task-harness/skills/task-build/SKILL.md) |
| 수용 조건과 실제 결과 대조 | [task-verify](plugins/task-harness/skills/task-verify/SKILL.md) |
| 명시 요청한 통합 흐름 설명과 최종 연습 | [task-understand](plugins/task-harness/skills/task-understand/SKILL.md) |
| 문서 정리 | [task-docs](plugins/task-harness/skills/task-docs/SKILL.md) |
| 이 지도 정리 | [task-agents](plugins/task-harness/skills/task-agents/SKILL.md) |
| Python 구현과 검토 | [python-best-practices](plugins/task-harness/skills/python-best-practices/SKILL.md) |
| React 구현과 검토 | [react-best-practices](plugins/task-harness/skills/react-best-practices/SKILL.md) |

현재 작업에 필요한 지침만 읽습니다. 작업 스킬은 명시 요청 시 사용하고, 기술 스킬은 해당 코드 작업에 적용합니다. 각 스킬 안에서도 현재 경계에 해당하는 참조만 읽으며 모든 스킬을 순서대로 호출하지 않습니다.
