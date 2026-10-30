---
name: python-best-practices
description: Use when writing or reviewing Python code that needs judgment beyond linters and type checkers, including architecture smells, validation, resource lifetime, async work, performance, tests, and failure handling.
license: Apache-2.0 AND MIT
---

# Python Best Practices

Python 코드의 구조, 성능, 테스트와 실패 처리를 검토하고 요청한 범위에서 개선합니다. Cisco 스킬의 짧은 진입점과 네 가지 상세 참조 구성을 사용합니다. 참조에는 적용 조건, BAD/GOOD 코드 예제와 체크리스트가 있습니다.

## How To Use This Skill

먼저 Python 지원 버전, 기존 의존성, 공개 인터페이스와 검사 설정을 확인한 뒤 현재 변경이 지나는 경계의 문서만 읽습니다. 예제는 Python 3.10 이상을 기준으로 하며, 외부 라이브러리 예제는 도입 요구가 아닙니다.

- 코드 구조, 설정, 재시도와 자원 소유권은 [Anti-Patterns](references/anti-patterns.md)를 읽습니다.
- CPU, 메모리, async와 대량 처리는 [Performance](references/performance.md)를 읽습니다.
- fixture, mock, 입력 경계와 실제 저장 검증은 [Testing](references/testing.md)을 읽습니다.
- 검증, 예외 변환, 부분 실패와 진행 보고는 [Error Handling](references/error-handling.md)을 읽습니다.

API 변경은 오류 처리와 테스트, async 변경은 성능과 자원 수명처럼 필요한 참조를 함께 사용합니다. 기존 로거와 도구를 우선 사용하되 직접 관리할 코드와 테스트를 줄이는 외부 패키지도 선택할 수 있습니다. 설치와 유지보수 비용을 함께 판단합니다.

## Review Focus

- I/O와 업무 규칙의 경계, 외부 입력과 공개 DTO를 확인합니다.
- 재시도 소유자, 전체 시도 예산, 멱등성과 취소 전파를 확인합니다.
- 연결과 파일의 소유권, async 경로의 차단 작업을 확인합니다.
- 예외가 원인을 보존하고 부분 성공을 숨기지 않는지 확인합니다.
- 성공 로그나 mock 호출뿐 아니라 출력과 실제 상태를 검증합니다.

검토 요청이면 위치, 재현 입력, 사용자 영향과 수정 방향을 반환하고 파일은 수정하지 않습니다. 구현 요청이면 필요한 변경과 기존 프로젝트의 검사를 수행합니다. 새 프레임워크나 테스트 도구로의 전환을 기본 해법으로 삼지 않습니다.

참조 전체를 답변에 복제하지 않습니다. 실행 결과와 미확인을 구분하며 타입 검사와 문법 검사를 런타임 동작 검증으로 보고하지 않습니다. 성능 개선은 측정 조건과 전후 결과가 있을 때만 주장합니다. 작업 보고는 별도 문서에 두며 AGENTS.md에 구현 현황을 추가하지 않습니다.

## Reference Map

| 관심사 | 상세 지침 |
| --- | --- |
| 구조, 설정, 자원과 흔한 실수 | [anti-patterns.md](references/anti-patterns.md) |
| 측정, 자료구조, 메모리와 async | [performance.md](references/performance.md) |
| 테스트 설계, fixture, mock와 실제 상태 | [testing.md](references/testing.md) |
| 입력, 예외, 부분 실패와 진행 보고 | [error-handling.md](references/error-handling.md) |

## Attribution

Cisco 및 wshobson의 원문을 수정해 포함합니다. 출처, 고정 리비전과 변경 내역은 [NOTICE](NOTICE), Apache 라이선스 전문은 [LICENSE](LICENSE)에 있습니다. 참조 자료의 MIT 고지도 NOTICE에 보존합니다.
