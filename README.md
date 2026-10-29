# Task Harness

작업을 분해하고 구현 과정을 정형화하기 위한 개인용 경량 하네스입니다. Codex에서 범위 결정, 구현, 검증, 문서 정비, 저장소 지침 관리를 다섯 스킬로 호출합니다. 같은 정보의 원본은 한 곳에 두고 문서를 연결합니다.

첫 사용자 흐름의 수용 조건이 정해지면 구현을 시작합니다. 전체 스펙 완성을 기다리지 않고, 구현 중 발견한 요구는 다음 작업에 반영합니다.

## 다섯 스킬

| 호출 | 역할 | 종료 조건 |
| --- | --- | --- |
| `$task-scope` | 질문 선별, 흐름별 작업 분해, 가정과 제외 범위 결정 | 사용자 행동, 성공 결과, 입력과 상태 변화, 실패 처리 확정 |
| `$task-build` | 작업 계약 작성, 구현, 주요 경계 검증 | 실행되는 흐름과 수용 조건의 검증 근거 확보 |
| `$task-verify` | 수용 조건별 구현 위치와 실제 관측 대조 | 통과, 실패, 미확인과 다음 행동 정리 |
| `$task-docs` | 문서 지도, 스펙, 플랜, ADR, 다이어그램 정비 | 현재 작업의 정보별 원본과 연결 확인 |
| `$task-agents` | 근거에 따른 짧은 `AGENTS.md` 생성과 갱신 | 기존 규칙 보존, 경로와 명령의 확인 상태 기록 |

스킬은 명시적으로 호출할 때 사용합니다. 단계마다 모두 호출할 필요는 없습니다. 확정된 작은 수정은 바로 `$task-build`로 시작할 수 있습니다. 각 스킬은 개별 설치해도 동작합니다.

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

플러그인 기능이 없고 프로젝트 스킬 로딩을 지원하는 환경에서는 다섯 디렉터리를 대상 프로젝트의 `.agents/skills/`로 복사합니다. 스킬의 참조 파일은 모두 각 디렉터리 안에 있습니다.

저장소 루트에서 다음을 실행합니다. `TARGET_PROJECT`는 실제 대상 프로젝트 경로로 바꿉니다. 같은 이름의 파일이나 링크가 있으면 복사를 중단합니다.

```sh
TARGET_PROJECT=/absolute/path/to/project
(
  set -eu
  test -d "$TARGET_PROJECT"
  for skill in task-scope task-build task-verify task-docs task-agents; do
    destination="$TARGET_PROJECT/.agents/skills/$skill"
    if [ -e "$destination" ] || [ -L "$destination" ]; then
      echo "Already exists: $destination" >&2
      exit 1
    fi
  done
  mkdir -p "$TARGET_PROJECT/.agents/skills"
  for skill in task-scope task-build task-verify task-docs task-agents; do
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
수정 범위, 실패 경계, 검증 명령을 짧게 기록하고 진행해줘.
```

```text
$task-verify
수용 조건마다 구현 위치와 현재 실행 근거를 연결해줘.
통과, 실패, 미확인을 구분하고 직접 확인이 필요한 조작과 기대 결과를 남겨줘.
```

```text
$task-docs $task-agents
기존 지침과 문서 경로를 보존하면서 현재 작업의 docs와 AGENTS.md를 정리해줘.
문서만 작성하고, 설정에서 확인한 명령과 실제 실행 결과를 구분해줘.
```

문서만 요청하면 제품 구현을 시작하지 않습니다. 문서와 구현을 함께 요청하면 첫 흐름의 수용 조건이 정해지는 즉시 구현으로 이어갑니다.

## 기록과 작업 방식

프로젝트에서 지정한 문서와 기존 경로를 우선합니다. 새 구조가 필요할 때는 아래 위치를 사용하며, 현재 작업에 필요한 파일만 만듭니다.

| 경로 | 정보의 원본 |
| --- | --- |
| `AGENTS.md` | 작업 지침, 확인한 명령, 탐색 경로 |
| `docs/README.md` | 현재 작업의 문서 지도 |
| `docs/specs/<topic>.md` | 기대 동작, 범위, 수용 조건, 미결사항과 가정 |
| `docs/plans/<topic>.md` | 구현 순서, 작업 담당과 상태, 경계, 검증 근거 |
| `docs/adr/0001-<decision>.md` | 결정과 근거, 대안, 구현, 검증과 한계 |
| `docs/diagrams/<topic>.*` | 그림이 필요한 구조와 흐름 |

기존 `docs/spec`, `docs/plan`, `WORK.md`나 별도 작업 장부는 보존합니다. 플랜은 요구 ID로 스펙을 참조하고, 기존 장부가 있으면 연결합니다. 같은 상태표를 두 곳에 만들거나 기존 기록을 자동 이관하지 않습니다. ADR과 다이어그램은 필요할 때만 추가합니다.

`AGENTS.md`는 실제 확인한 경로와 명령만 기록합니다. 설정 확인, 실행 성공, 실행 실패, 미확인을 구분하고 기존 override와 적용 범위를 확인합니다.

- [문서 템플릿](plugins/task-harness/skills/task-docs/references/document-templates.md)
- [저장소 지침 템플릿](plugins/task-harness/skills/task-agents/references/agents-template.md)
- [다이어그램 지침](plugins/task-harness/skills/task-docs/references/diagrams.md)
- [한 파일 기록용 템플릿](plugins/task-harness/skills/task-scope/references/work-template.md)
- [선택적 위임 계약](plugins/task-harness/skills/task-build/references/delegation-template.md)
- [검증 기록](plugins/task-harness/skills/task-verify/references/verification-template.md)

메인 에이전트 한 명으로 시작합니다. 인터페이스가 확정된 독립 작업이나 검토에 한해 보조 에이전트를 고려하고, 도구가 없으면 순차 수행합니다. 문서 초안을 위임할 때도 파일마다 편집 책임자를 한 명 정하고 메인이 최종 통합합니다.

## 구성과 실행 범위

배포물은 Markdown, JSON, YAML과 외부 자산이 없는 SVG 예시로 구성합니다. GSD와 Superpowers, 별도 모델, MCP, hooks, 자동 업데이트, 외부 로그 전송에 의존하지 않습니다. Push, PR 생성, 배포, 브라우저 자동 조작은 기본 작업 절차에 포함하지 않습니다.

하네스 자체에는 외부 서비스 실행 코드가 없습니다. Codex의 모델 통신과 대상 프로젝트의 패키지 설치는 별도입니다. 스킬 지침은 실행 환경의 권한이나 격리를 새로 제공하지 않습니다.

`local*` 파일과 `.local/` 실행 자료는 Git에서 제외합니다. 공개 패키지는 `plugins/task-harness/`, 카탈로그는 `.agents/plugins/marketplace.json`입니다. 배포에는 [MIT 라이선스](LICENSE)를 적용합니다.

## 검증

패키지 검사는 Python 3.10 이상에서 추가 패키지 없이 실행합니다. Python은 하네스 사용 의존성이 아닙니다.

```sh
python3 -m unittest discover -s tests -v
```

검사 범위는 카탈로그 경로와 매니페스트 연결, 다섯 스킬의 명시 호출 정책, 개별 복사 후 참조 유지, 배포 파일 구성, README의 로컬 링크, SVG의 외부 참조와 실행 요소 부재입니다. 정적 검사만으로 에이전트의 판단이나 모든 Codex 버전의 호환성을 보장하지 않습니다.

2026-10-30에 macOS, Python 3.14.0, Codex CLI 0.165.0에서 확인했습니다. 다른 버전의 호환성은 별도 확인이 필요합니다.

| 항목 | 상태 | 근거 |
| --- | --- | --- |
| 로컬 CLI와 플러그인 명령 | 확인 | `codex-cli 0.165.0`, `codex plugin --help` |
| 패키지 검사 | 통과 | 표준 라이브러리 검사 6개 통과, 개별 복사 후 참조 확인 |
| 스킬 형식 검사 | 통과 | `skill-creator`의 `quick_validate.py`로 다섯 스킬 확인 |
| 임시 환경의 플러그인 설치 | 통과 | 마켓플레이스 등록, `0.2.0` 설치, `installed: true`, `enabled: true`, 다섯 스킬 캐시 확인 |
| 기존 세 스킬의 동작 시나리오 | 확인 | 질문 종료, 검증 실행 실패, 순차 작업, 범위 결정만 요청, 검토만 요청의 모의 검사 |
| 문서 스킬의 합성 저장소 검사 | 확인 | 문서 3개만 생성 또는 갱신, 기존 경로와 사용자 규칙 보존, 명령 미실행 명시, 장부 중복 없음 |
| 다이어그램과 ADR 변경 상황 | 모의 확인 | 오래된 SVG의 갱신 필요 표시, ADR 대체 관계와 스펙 갱신 |
| SVG 예시 표시 | 확인 | macOS Quick Look 렌더링 후 글자와 연결선, 잘림 확인 |
| 실제 UI에서 스킬 선택과 새 대화 호출 | 미확인 | 직접 확인 필요 |
| 원격 커밋 설치와 공개 디렉터리 게시 | 미실행 | 로컬 구축 범위 |

설치 검증은 인증과 사용자 설정을 복사하지 않은 임시 Codex 상태 경로에서 수행했습니다. 실제 사용자 설정에는 설치하지 않았습니다. 동작 검사는 독립 에이전트의 모의 응답과 합성 저장소 문서 작업으로 구분합니다. 대상 앱 구현이나 UI 명시 호출을 실행한 검사는 아닙니다. 작업 시간 절약 효과는 측정하지 않았습니다.

형식 참고: [공식 플러그인 패키징 문서](https://developers.openai.com/plugins/build/plugins), [공식 스킬 문서](https://learn.chatgpt.com/docs/build-skills), [공식 AGENTS.md 지침](https://learn.chatgpt.com/docs/agent-configuration/agents-md).
실제 지원 범위는 사용 중인 Codex에서 확인합니다.
