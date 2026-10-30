# Task Harness

작업을 분해하고 구현 과정을 정형화하기 위한 개인용 경량 하네스입니다. Codex에서 범위 결정, 구현, 검증, 이해 확인, 문서 정비, 저장소 지침 관리를 작업 스킬 6개로 호출하고, Python과 React 구현에는 기술 스킬 2개를 사용합니다. 같은 정보의 원본은 한 곳에 두고 문서를 연결합니다.

사용자의 행동 순서와 상태 변화가 기대대로 동작하는지 실행 근거로 검증하는 것이 관측 가능성을 챙기는 목적입니다. 첫 사용자 흐름의 수용 조건이 정해지면 구현을 시작합니다. 전체 스펙 완성을 기다리지 않고, 구현 중 발견한 요구는 다음 작업에 반영합니다.

## 여덟 스킬

| 호출 | 역할 | 종료 조건 |
| --- | --- | --- |
| `$task-scope` | 질문 선별, 흐름별 작업 분해, 가정과 제외 범위 결정 | 사용자 행동, 성공 결과, 입력과 상태 변화, 실패 처리 확정 |
| `$task-build` | 실행 기록 준비, 구현, 주요 경계 검증 | 실행되는 흐름과 수용 조건의 검증 근거 확보 |
| `$task-verify` | 수용 조건별 구현 위치와 실제 관측 대조 | 통과, 실패, 미확인과 다음 행동 정리 |
| `$task-understand` | 사람 검증 뒤 한 질문씩 이해 확인, 설명과 예제 및 최종 점검 | 선택한 사례의 설명 확인과 남은 항목 정리 |
| `$task-docs` | 문서 지도, 스펙, 체크리스트, 작업 보고, ADR, 다이어그램 정비 | 현재 작업의 정보별 원본과 연결 확인 |
| `$task-agents` | 문서 작성 규칙과 스킬 사용 시점을 담은 룰북 지도 | 기존 규칙 보존, 실제 문서와 스킬 연결 |
| `$python-best-practices` | Python 입력, 저장, 예외, 자원과 동시성 검토 | 변경 경계에 맞는 구현 또는 검토 근거 |
| `$react-best-practices` | React 상태, Effect, 폼과 사용자 조작 검토 | 변경한 화면 흐름의 구현 또는 검토 근거 |

작업 스킬 6개는 명시적으로 호출할 때 사용합니다. Python과 React 스킬은 해당 코드를 작성하거나 검토할 때 자동 선택을 허용하며, 명시적으로도 호출할 수 있습니다. 단계마다 모두 호출할 필요는 없습니다. 확정된 작은 수정은 바로 `$task-build`로 시작할 수 있습니다. 각 스킬은 개별 설치해도 동작합니다.

## 설치

먼저 현재 설치의 지원 명령을 확인합니다.

```sh
codex --version
codex plugin --help
```

### 로컬 플러그인

이 저장소 루트에서 실행합니다. 아래 명령은 현재 사용자의 Codex에 마켓플레이스와 플러그인을 등록합니다.

```sh
codex plugin marketplace add .
codex plugin add task-harness@jincy7-tools
codex plugin list --marketplace jincy7-tools --json
```

새 Codex 세션에서 스킬을 확인합니다. 기존에 같은 이름의 마켓플레이스가 있으면 등록 경로를 먼저 확인합니다. 플러그인 캐시에 복사된 설치본은 원본 수정만으로 갱신됐다고 가정하지 않고 설치된 내용을 확인합니다.

### 프로젝트 스킬로 복사

플러그인 기능이 없고 프로젝트 스킬 로딩을 지원하는 환경에서는 여덟 디렉터리를 대상 프로젝트의 `.agents/skills/`로 복사합니다. 스킬의 참조 파일은 모두 각 디렉터리 안에 있습니다.

저장소 루트에서 다음을 실행합니다. `TARGET_PROJECT`는 실제 대상 프로젝트 경로로 바꿉니다. 같은 이름의 파일이나 링크가 있으면 복사를 중단합니다.

```sh
TARGET_PROJECT=/absolute/path/to/project
(
  set -eu
  test -d "$TARGET_PROJECT"
  for skill in task-scope task-build task-verify task-docs task-agents task-understand python-best-practices react-best-practices; do
    destination="$TARGET_PROJECT/.agents/skills/$skill"
    if [ -e "$destination" ] || [ -L "$destination" ]; then
      echo "Already exists: $destination" >&2
      exit 1
    fi
  done
  mkdir -p "$TARGET_PROJECT/.agents/skills"
  for skill in task-scope task-build task-verify task-docs task-agents task-understand python-best-practices react-best-practices; do
    cp -R "plugins/task-harness/skills/$skill" "$TARGET_PROJECT/.agents/skills/"
  done
)
```

플러그인 설치와 프로젝트 복사 중 한 경로를 선택합니다. 중복 설치는 같은 이름의 스킬을 둘 이상 노출할 수 있습니다. 환경 정책으로 차단된 기능을 복사 방식으로 우회하지 않습니다. 스킬 로딩도 지원하지 않으면 필요한 `SKILL.md`를 직접 읽도록 요청할 수 있습니다. 기존 `AGENTS.md`는 유지합니다.

### Git 마켓플레이스

원격에 공개한 커밋이 있을 때 사용하는 배포 경로입니다. `RELEASE_SHA`에 검증한 전체 커밋 SHA를 지정합니다. 존재하지 않는 릴리스나 태그를 설치 대상으로 가정하지 않습니다.

```sh
RELEASE_SHA=replace-with-published-commit-sha
codex plugin marketplace add Jincy7/task-harness --ref "$RELEASE_SHA"
codex plugin add task-harness@jincy7-tools
```

## 사용

```text
$task-scope
현재 요청과 코드를 읽고 첫 번째로 실행할 사용자 흐름을 정해줘.
구현 결정을 바꾸는 질문, 가정하고 진행할 항목, 보류할 항목을 구분해줘.
첫 흐름의 수용 조건이 정해지면 구현까지 이어가줘.
```

```text
$task-build
확정된 흐름을 입력부터 저장과 결과 표시까지 구현해줘.
로거가 없는 상태에서 필요한 행동 시나리오와 관측 지점을 먼저 정해줘.
표준 기능과 외부 패키지 중 직접 관리할 코드가 줄어드는 쪽으로 기록을 준비해줘.
실행 후 이상 상황의 근거, 원인과 조치, 재검증 결과는 별도 보고서에 남겨줘.
```

```text
$task-verify
수용 조건마다 구현 위치와 현재 실행 근거를 연결해줘.
통과, 실패, 미확인을 구분하고 직접 확인이 필요한 조작과 기대 결과를 남겨줘.
```

```text
$task-docs $task-agents
기존 지침과 문서 경로를 보존하면서 현재 작업의 docs와 AGENTS.md를 정리해줘.
AGENTS.md에는 문서 작성 규칙과 스킬 사용 시점만 연결해줘.
플랜은 체크리스트로 유지하고 결과와 검증 근거는 별도 작업 보고에 남겨줘.
```

```text
$task-build $python-best-practices
이 Python 저장 흐름을 구현하고 입력 검증, 롤백과 재시도를 확인해줘.
```

```text
$react-best-practices
이 React 검색 화면을 검토만 해줘. 상태 소유권, 늦은 응답과 입력값 보존을 확인해줘.
```

문서만 요청하면 제품 구현을 시작하지 않습니다. 문서와 구현을 함께 요청하면 첫 흐름의 수용 조건이 정해지는 즉시 구현으로 이어갑니다.

### 웨이브별 이해 확인

```text
$task-understand
이번 작업은 웨이브마다 사람 검증을 마친 뒤 이해를 확인해줘.
질문은 하나씩 하고, 부족하면 설명과 예제를 준 뒤 다른 사례로 확인해줘.
내가 확인하는 버전을 유지하면서 독립적인 구현과 검증은 이어가고,
마지막에는 최신 구현의 전체 흐름과 앞서 혼동한 부분을 점검해줘.
```

플러그인에서 이름에 네임스페이스가 표시되면 `$task-harness:task-understand`로 호출합니다. 이번 웨이브만 확인하거나 최종 점검만 요청할 수도 있습니다.
작업 스킬의 `allow_implicit_invocation`은 false입니다. 한 번 요청한 웨이브별 확인은 현재 작업에서 유지하므로 매번 재호출할 필요는 없습니다. 관련 없는 작업에서는 자동으로 문답을 시작하지 않습니다.

흐름은 `구현 및 자동 검증 → 준비된 사람 검증 → 질문 → 응답 → 필요한 설명과 예제 → 변형 사례 → 웨이브 정리`입니다. 마지막에는 최신 구현으로 전체 흐름을 다시 확인합니다.
사람 검증 대기나 실패를 문답 완료로 덮지 않으며 제품 상태와 이해 확인 상태를 분리합니다. 확인 중인 화면, 입력과 코드 버전을 유지하고 독립 작업을 진행합니다. 실행 환경에서 병행할 수 없으면 교대로 수행합니다.

대화 규칙과 선택적 상세 예시는 [task-understand](plugins/task-harness/skills/task-understand/SKILL.md)에서 확인합니다. 문답 원문은 복제하지 않고 기존 작업 보고에 요지와 남은 확인만 기록합니다.

## 기록과 작업 방식

프로젝트에서 지정한 문서와 기존 경로를 우선합니다. 새 구조가 필요할 때는 아래 위치를 사용하며, 현재 작업에 필요한 파일만 만듭니다.

| 경로 | 정보의 원본 |
| --- | --- |
| `AGENTS.md` | 문서 작성 규칙과 스킬 선택 지도 |
| `docs/README.md` | 현재 작업의 문서 지도 |
| `docs/specs/<topic>.md` | 기대 동작, 범위, 수용 조건, 미결사항과 가정 |
| `docs/plans/<topic>.md` | 작업 체크리스트와 스펙 및 보고서 링크 |
| `docs/reports/<topic>/<work-id>.md` | 작업별 결과, 검증 근거, 이상 상황의 원인과 해결 |
| `.local/runs/<run-id>/` | Git에서 제외하는 원본 로그, 명령 출력과 실행 결과 |
| `docs/adr/0001-<decision>.md` | 결정과 근거, 대안, 구현, 검증과 한계 |
| `docs/diagrams/<topic>.*` | 그림이 필요한 구조와 흐름 |

기존 `docs/spec`, `docs/plan`, `WORK.md`나 별도 작업 장부는 보존합니다. 플랜은 요구 ID로 스펙을 참조하고 완료 항목에는 작업 보고를 연결합니다. 기존 장부의 이력은 보존하고 보고서에서 연결합니다. 같은 상태표를 두 곳에 만들거나 기존 기록을 자동 이관하지 않습니다. ADR과 다이어그램은 필요할 때만 추가합니다.

`AGENTS.md`에는 문서를 어떻게 쓰고 언제 무슨 스킬을 읽을지 연결합니다. 실행 방법은 README, 체크 상태는 플랜, 결과와 검증 근거는 작업 보고에서 관리합니다. 기존 사용자 규칙과 override의 적용 범위는 보존합니다. 새로 생성하는 지침에는 구현 여부나 테스트 부재 목록을 넣지 않습니다.

- [문서 템플릿](plugins/task-harness/skills/task-docs/references/document-templates.md)
- [저장소 지침 템플릿](plugins/task-harness/skills/task-agents/references/agents-template.md)
- [다이어그램 지침](plugins/task-harness/skills/task-docs/references/diagrams.md)
- [범위 정리용 템플릿](plugins/task-harness/skills/task-scope/references/work-template.md)
- [선택적 위임 계약](plugins/task-harness/skills/task-build/references/delegation-template.md)
- [검증 기록](plugins/task-harness/skills/task-verify/references/verification-template.md)

메인 에이전트 한 명으로 시작합니다. 인터페이스가 확정된 독립 작업이나 검토에 한해 보조 에이전트를 고려하고, 도구가 없으면 순차 수행합니다. 문서 초안을 위임할 때도 파일마다 편집 책임자를 한 명 정하고 메인이 최종 통합합니다.

## 실행 기록부터 시작하는 흐름

1. 사전 상태, 행동 순서, 기대 상태 전이와 결과를 정합니다. 기존 로거가 있으면 우선 재사용하고, 없으면 필요한 관측 기능에 맞춰 표준 기능이나 외부 패키지를 선택합니다. 첫 실행 전에 기록 연결을 확인합니다.
2. 확정된 흐름을 구현하고 행동, 요청, 저장과 결과를 실행 및 사례 ID로 연결합니다. 정상 흐름과 현재 요구에 관련된 수정, 중복 조작, 실패 후 재시도 등을 실행합니다.
3. 기대값을 실제 응답, 화면이나 독립적인 저장 상태 조회와 대조합니다. 예외, 예상 밖 종료, timeout과 로그 누락을 확인하고, 사전에 의도한 실패는 실제 이상 상황과 구분합니다.
4. 작업 보고에 현상, 근거, 원인 가설 또는 확인된 원인, 조치와 재검증을 기록합니다. 플랜에는 체크 상태와 보고서 링크만 바꿉니다.

로거가 없는 새 프로젝트를 일반적인 시작 상황으로 봅니다. 무의존성을 강제하지 않으며, 설치와 유지보수 부담을 포함해 직접 관리할 코드와 테스트가 줄어들면 외부 패키지를 선택합니다. 기존 로거가 있으면 우선 재사용합니다. OTEL도 필요한 추적 범위와 비용으로 판단합니다. 외부 패키지 도입이 외부 수집 서비스 도입을 뜻하지는 않습니다.

관측 지표는 로그 개수나 오류 부재가 아니라 행동과 실제 결과를 연결할 근거입니다. 구현의 success 로그만으로 통과시키지 않으며 UI, API 통합, 단위와 합성 계측 검증의 범위를 구분합니다. 수집이 불완전하면 그 근거에 의존한 조건을 미확인으로 남깁니다.

플랜은 `- [ ]` 체크리스트로 유지합니다. 검증 실행기가 결과를 플랜에 쓰지 않게 하고, 실행별 원본은 `.local/`, 사람이 읽을 요약은 작업별 보고서에 둡니다. 보고서도 매 명령이나 후속 작업을 계속 덧붙이는 일지로 만들지 않습니다.

- [로컬 실행 기록과 이상 후보 확인](plugins/task-harness/skills/task-build/references/runtime-logging.md)
- [작업 보고와 해결 기록](plugins/task-harness/skills/task-verify/references/verification-template.md)

## 구성과 실행 범위

배포물은 Markdown, JSON, YAML과 외부 자산이 없는 SVG 예시로 구성합니다. GSD와 Superpowers, 별도 모델, MCP, hooks, 자동 업데이트, 외부 로그 전송에 의존하지 않습니다. Push, PR 생성, 배포, 브라우저 자동 조작은 기본 작업 절차에 포함하지 않습니다.

하네스 자체에는 외부 서비스 실행 코드가 없습니다. Codex의 모델 통신과 대상 프로젝트의 패키지 설치는 별도입니다. 스킬 지침은 실행 환경의 권한이나 격리를 새로 제공하지 않습니다.

`local*` 파일과 `.local/` 실행 자료는 Git에서 제외합니다. 공개 패키지는 `plugins/task-harness/`, 카탈로그는 `.agents/plugins/marketplace.json`입니다. 배포에는 [MIT 라이선스](LICENSE)를 적용합니다.

## 검증

패키지 검사는 Python 3.10 이상에서 추가 패키지 없이 실행합니다. Python은 하네스 사용 의존성이 아닙니다.

```sh
python3 -m unittest discover -s tests -v
```

검사 범위는 카탈로그와 매니페스트 연결, 여덟 스킬의 호출 정책, 개별 복사 후 로컬 참조 유지, 배포 파일 구성, README의 로컬 링크, SVG의 외부 참조와 실행 요소 부재입니다. 공식 출처 링크는 선택 참고 자료이며 실제 지침은 스킬 안에 포함합니다. 정적 검사만으로 에이전트 판단이나 모든 Codex 버전의 호환성을 보장하지 않습니다.

### 검증 이력

`0.2.0`은 2026-10-30에 macOS, Python 3.14.0, Codex CLI 0.165.0에서 패키지 검사 6개와 스킬 형식 검사를 통과했습니다.
임시 환경과 사용자 환경의 플러그인 설치, 원격 커밋 설치를 확인했습니다.
Docker의 실제 세션에서는 agents, scope, build, docs 호출을 관측했고 생성 앱의 테스트 5개와 독립 CLI 사례 30개를 복사본에서 통과했습니다.
별도 verify 호출과 실제 브라우저 흐름은 확인하지 않았습니다.

`0.3.0`은 2026-10-30에 패키지 검사 6개와 스킬 7개의 형식 검사를 통과했습니다. 독립 에이전트의 합성 저장소 작업에서 기존 사용자 규칙 보존, 상태 기록 분리와 지도 링크 12개를 확인했습니다.
Python 검토 예제에서는 실제 SQLite로 거짓 성공과 입력 검증 결함을 재현했습니다. React 검토 예제에서는 query 의존성 누락과 index key에 따른 편집 상태 문제를 코드로 확인했습니다. 두 검토 모두 대상 소스를 수정하지 않았습니다.
React 실행과 브라우저 검증, 새 세션에서 기술 스킬의 자동 선택은 확인하지 않았습니다. 이 검토는 합성 예제의 동작 확인이며 실제 프로젝트 전반의 품질 보장은 아닙니다.

`0.4.0`은 실행 기록 준비와 작업 보고 분리를 반영합니다.
패키지 검사 6개와 스킬 7개의 형식 검사를 통과했습니다.
표준 라이브러리 합성 CLI에서 테스트 9개와 실행 사례 18개로 JSON stdout, 종료 코드, 예상 실패, 로그 쓰기 실패 시 업무 결과 보존과 실행 ID 분리를 확인했습니다.
검증 전후 플랜이 변경되지 않고 완료 체크와 보고서 링크만 별도로 갱신되는 것도 확인했습니다.

로그 수집과 이상 후보 판정은 대상 프로젝트에서 구현하고 확인하는 절차이며, 이 플러그인 자체가 상주 로거나 자동 감시 서비스를 실행하지 않습니다. 합성 검증은 운영 환경, 디스크 고갈이나 강제 종료, 실제 UI와 자동 스킬 발견까지 확인한 결과는 아닙니다.

`0.5.0`은 로거 없는 프로젝트의 도구 선택과 행동 패턴에 따른 검증 근거를 명확히 했습니다. 패키지 검사 6개와 스킬 7개의 형식 검사를 통과했습니다.
독립 에이전트의 합성 상황 3개에서 외부 패키지 선택, 성공 로그와 저장 상태의 불일치, 일부 로그 누락 시 판정 범위 구분을 확인했습니다. 이 검토에서 외부 로깅 패키지 설치나 실제 앱 실행은 수행하지 않았습니다.

`0.6.0`은 명시 호출용 task-understand와 웨이브별 사람 검증 이후의 문답, 최종 점검을 추가합니다. 규칙 정정과 변형 사례, 실패 출력 보존 지침도 보강했습니다.
2026-10-30에 패키지 검사 6개와 스킬 8개의 형식 검사를 통과했습니다. 독립 에이전트의 합성 문답 사례 7개를 검토하고, 문답의 제품 수정 범위를 명확히 한 뒤 설명 전용 및 종료 사례 2개를 재검증했습니다.
추가 합성 상황 4개에서 규칙 정정, 외부 검사 실패의 근거 부족, 고정 가중치의 불변 조건, stdout 오류 보존 설계를 확인했습니다. 실제 앱 재실행, 실제 사용자 이해 및 모든 환경의 병행 실행을 검증한 결과는 아닙니다.

## 참고 자료

[Python 스킬 구성 참고](https://github.com/cisco-open/ai-harness-toolkit/tree/main/skills/python-best-practices)의 짧은 진입점과 관심사별 참조 구조를 참고했습니다.
본문의 지침은 이 하네스에 맞게 새로 작성했으며 해당 저장소의 스킬 원문을 배포물에 복사하지 않았습니다. Python과 React 공식 근거는 각 기술 스킬의 참조 문서에서 연결합니다.

형식 참고: [공식 플러그인 패키징 문서](https://developers.openai.com/plugins/build/plugins), [공식 스킬 문서](https://learn.chatgpt.com/docs/build-skills), [공식 AGENTS.md 지침](https://learn.chatgpt.com/docs/agent-configuration/agents-md).
실제 지원 범위는 사용 중인 Codex에서 확인합니다.
