# 로컬 실행 기록

처음 실행하기 전에 기록 경로를 준비하고 실행이 끝난 뒤 이상 후보를 확인합니다. 목적은 실패를 재현하고 수정 전후를 연결하는 것입니다. 로그 수집과 원인 판단, 기능 검증은 별개입니다.

## 도구 선택

| 현재 상황 | 기본 선택 |
| --- | --- |
| 기존 로거와 검증 실행기 존재 | 기존 도구에 필요한 필드와 출력 경로만 보완 |
| 작은 Python 앱 | 표준 `logging`, JSON formatter와 파일 handler |
| 작은 Node 앱 | 기존 logger 또는 작은 JSON 직렬화와 파일 stream |
| 브라우저 화면 | 기존 console, 오류 경계와 테스트 도구의 console 및 page error 수집 |
| 실제 서비스 간 추적이나 기존 관측 플랫폼 연동 요구 | 그 요구가 있을 때 OTEL 검토 |

로컬 기록만을 위해 OTEL SDK, collector, 대시보드나 상시 감시 프로세스를 설치하지 않습니다.
기존 OTEL을 이 지침만으로 제거하지도 않습니다.
logger 교체가 필요하면 요청 범위와 기존 출력 계약을 먼저 확인합니다.
React의 브라우저 console은 자동으로 서버 파일에 저장되지 않으므로 수집하지 않은 화면 오류는 미확인입니다.
별도 브라우저 전송 API를 기본으로 만들지 않습니다.

## 저장과 상관관계

기존 경로를 우선합니다. 새 프로젝트의 기본 예시는 다음과 같습니다.

```text
.local/runs/<run-id>/
  events-<process-id>.jsonl
  <command-id>.stdout.log
  <command-id>.stderr.log
  result.json
```

앱 시작이나 검증 실행마다 새로운 `run_id`를 사용하고, 같은 실행에 속한 자식 프로세스에는 그 ID를 전달합니다.
장시간 실행 앱과 별도 검증의 run ID가 다르면 요청 ID와 양쪽 실행 ID로 연결합니다.
검증 실행이 여러 독립 CLI 실행을 묶으면 보고서에 그 실행 ID 목록을 연결합니다.
같은 run ID를 공유하는 사례는 `case_id`로 구분합니다.
원본 파일은 덮어쓰지 않습니다.
기존 `.gitignore`를 보존하면서 `.local/` 제외를 확인합니다.

공통 필드는 `schema_version`, UTC ISO 시각 `ts`, `level`, `event`, `run_id`, `origin`, `component`, `outcome`입니다.
`origin`은 `application`, `verification`, `setup`을 구분합니다.
요청이나 작업을 연결할 때만 `operation_id`, 실패에는 `error_code`, 필요하면 `duration_ms`, `case_id`를 추가합니다.
문맥 전파가 필요하지 않은 앱에 trace/span 계층을 새로 만들지 않습니다.

```json
{"schema_version":1,"ts":"2026-10-30T02:00:00Z","level":"ERROR","event":"storage.write_failed","run_id":"run-01","origin":"application","component":"storage","outcome":"failed","operation_id":"op-03","error_code":"WRITE_FAILED"}
```

업무 이벤트는 요청 결과와 저장 커밋 또는 롤백 같은 경계에 둡니다. 정상 완료는 INFO, 복구 가능한 이상은 WARN, 예상 밖 실패는 ERROR로 구분합니다. 검증에서 유도한 오류도 실제 결과는 보존하며 해당 case의 사전 정의된 기대 결과와 함께 해석합니다.

각 프로세스는 자기 파일에 쓰는 방식을 우선합니다.
같은 파일에 여러 프로세스가 쓰게 하려면 하나의 writer나 실제 검증한 조정 방법을 사용합니다.
일반 파일 handler가 프로세스 간 회전까지 안전하다고 가정하지 않습니다.
크기 제한과 보존 개수를 정하고, 보고서에서 참조한 실행은 정리 전에 보존합니다.
긴 실행은 예를 들어 파일당 5 MiB, 프로세스당 보관 3개로 시작하되 현재 환경에 맞게 조정합니다.

## 로그가 업무 결과를 바꾸지 않도록

CLI stdout이 JSON 계약이면 진단 로그를 섞지 않습니다. stderr 또는 별도 파일을 사용하고 stdout과 stderr를 따로 수집합니다. 명령 수집기는 실제 하위 프로세스의 종료 코드, timeout과 signal을 보존합니다. `tee`의 성공이나 stderr의 문자열 검색만으로 실행 성공을 판정하지 않습니다.

기록 필드는 허용 목록으로 제한합니다. 인증 정보, 환경 변수 전체, 요청 본문, 사용자 원문과 민감한 명령 인자를 자동 기록하지 않습니다. 오류 메시지와 stack도 민감한 값이 섞일 수 있으므로 안전한 코드와 필요한 위치를 우선하고 원문은 필요한 범위만 정제해 보관합니다.

로그 쓰기 실패는 원래 업무 결과를 유지하면서 안전한 stderr 알림과 `capture_status=partial` 또는 `unavailable`로 드러냅니다. 실패한 로거에 다시 오류를 기록하는 재귀를 피합니다.
수집 상태는 실행 결과 파일의 `capture_status`와 작업 보고에 남깁니다. 결과 파일도 쓸 수 없으면 stderr와 최종 응답에 기록 실패를 알립니다. 업무용 stdout 스키마에는 임의 필드를 추가하지 않습니다.
수집 실패와 제품 실패는 구분하며, 근거가 없는 조건을 완료로 바꾸지 않습니다.

## 첫 연결 확인

현재 언어와 기존 테스트 도구로 필요한 항목만 검사합니다. 안전한 실패는 임시 경로와 테스트 대역에서 유도하거나 `origin=setup`의 합성 오류 이벤트로 확인합니다. 실제 사용자 데이터를 손상시키지 않으며, 합성 이벤트가 남은 사실을 업무 실패 처리의 검증으로 보고하지 않습니다.

- 시작 이벤트와 안전하게 유도한 실패가 JSONL 한 줄씩 읽히는지 확인
- CLI stdout, 원래 종료 코드와 업무 실패 결과 보존
- 실제로 사용하는 스레드 또는 프로세스 방식에서 줄 손상과 수명 확인
- 쓰기 불가 위치에서 수집 실패가 보이는지 확인
- 민감한 입력이 출력 필드에 섞이지 않는지 확인

로거가 이미 있고 이번 변경이 이 경계에 영향을 주지 않으면 같은 준비 작업을 반복하지 않습니다.

## 이상 후보 확인과 작업 보고

실행 종료나 작업 흐름의 확인 지점에서 다음을 확인합니다. 기존 실행기가 있으면 이 규칙을 보완하고, 없으면 현재 명령 결과와 JSONL을 읽어 판단합니다. 파일을 만든 사실만으로 탐지가 자동화됐다고 주장하지 않습니다.

| 신호 | 처리 |
| --- | --- |
| 미처리 예외, 예상 밖 종료 코드나 signal, 5xx | 이상 후보, 재현과 관련 요청 확인 |
| timeout 또는 명시된 시간 예산 초과 | 지연 후보, 예산과 실제 시간 기록 |
| assertion 실패나 상태 불변식 위반 | 해당 수용 조건 실패, 입력과 저장 상태 연결 |
| 사전 정의된 실패 테스트의 예상 오류 | 예상 동작, assertion이 통과했을 때만 해당 조건 통과 |
| 누락되거나 깨진 로그, 시작만 있고 종료 결과 없음 | 수집 또는 실행 미확인, 성공 추론 금지 |

WARN/ERROR만이 아니라 `outcome`, 종료 코드와 assertion을 함께 봅니다. 테스트 origin이라는 이유만으로 오류를 전부 제외하지 않습니다. 같은 오류는 코드와 경계별로 묶고 횟수 및 대표 증거만 보고서에 적습니다. 느림의 기준이나 원인은 로그만으로 만들어내지 않습니다.

작업 보고에는 현상, 실행 ID와 근거 위치, 기대와 실제, 가설과 확인된 원인, 수행한 조치와 제안, 수정 후 재검증을 구분합니다. 단지 오류가 사라졌다는 이유로 해결 처리하지 않습니다. 해결되지 않은 항목에는 다음 확인을 남깁니다. 플랜에는 체크 상태와 보고서 링크만 갱신합니다.

공식 참고:

- [Python handler와 파일 회전](https://docs.python.org/3/library/logging.handlers.html)
- [Python 프로세스 간 로그 기록](https://docs.python.org/3/howto/logging-cookbook.html#logging-to-a-single-file-from-multiple-processes)
- [Node console의 stream과 I/O 특성](https://nodejs.org/api/console.html)
- [OTEL의 계측 구성](https://opentelemetry.io/docs/languages/python/instrumentation/)

위 링크는 구현 세부 확인용입니다. 현재 작업에 필요한 지침은 이 파일에 포함되어 있습니다.
