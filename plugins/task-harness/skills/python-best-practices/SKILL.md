---
name: python-best-practices
description: Use when writing or reviewing Python code involving validation, persistence, exceptions, resource lifetime, async work, performance, or test boundaries.
---

# Python Best Practices

Python 코드의 입력, 실패 처리, 자원 수명과 테스트 경계를 검토하고 요청한 범위에서 개선합니다. 저장소의 Python 지원 버전, 의존성, 기존 구현과 검사 설정을 먼저 확인합니다. 새 프레임워크나 도구 도입을 기본 해법으로 삼지 않습니다.

## 필요한 지침 선택

| 작업 | 읽을 지침 |
| --- | --- |
| 입력 검증, 업무 로직, 예외, 저장, 테스트 | [경계와 테스트](references/boundaries-and-tests.md) |
| 파일과 연결 수명, async, 취소, 대량 처리, 성능 | [자원과 동시성](references/resources-and-concurrency.md) |

현재 변경이 지나는 경계만 확인합니다. 검토 요청이면 문제 위치, 재현 입력, 사용자에게 미치는 영향과 수정 방향을 반환하고 파일은 수정하지 않습니다. 구현 요청이면 기존 공개 인터페이스를 유지하면서 필요한 변경과 검증을 수행합니다.

## 검증과 반환

기존 프로젝트의 검사 명령을 사용합니다. 입력 경계, 실패 후 상태, 재시도와 자원 정리를 변경에 맞게 검증합니다. 테스트 프레임워크를 교체하거나 불필요한 의존성을 추가하지 않습니다. 타입 검사와 문법 검사를 런타임 동작 검증으로 보고하지 않습니다.

변경 또는 발견 사항, 실제 실행 결과, 미확인 조건을 간결하게 반환합니다. 성능 개선은 측정 조건과 전후 결과가 있을 때만 주장합니다. 작업 결과와 검증 근거는 별도 작업 보고에 두고 AGENTS.md에 구현 현황을 추가하지 않습니다.
