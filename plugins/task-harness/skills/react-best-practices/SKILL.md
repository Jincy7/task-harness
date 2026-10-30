---
name: react-best-practices
description: Use when writing or reviewing React components and Hooks involving state ownership, Effects, asynchronous UI, forms, accessibility, rendering performance, or server/client boundaries.
---

# React Best Practices

React 화면의 상태, 비동기 처리와 사용자 조작을 검토하고 요청한 범위에서 개선합니다. React 버전, 프레임워크와 라우터, 렌더링 방식, Compiler와 기존 검사 설정을 먼저 확인합니다. 이 스킬은 React를 사용하지 않는 화면에 React 도입을 요구하지 않습니다.

## 필요한 지침 선택

| 작업 | 읽을 지침 |
| --- | --- |
| 상태 소유권, Hooks, Effect, 요청 경쟁, 렌더링 | [상태와 Effect](references/state-and-effects.md) |
| 폼, 접근성, 서버 경계, UI 검증 | [화면 경계와 테스트](references/boundaries-and-tests.md) |

현재 변경에 필요한 지침만 읽습니다. 검토 요청이면 문제 위치, 재현 조작, 사용자 영향과 수정 방향을 반환하고 파일은 수정하지 않습니다. 구현 요청이면 기존 컴포넌트와 데이터 흐름을 따라 수정하며, 상태 관리 라이브러리나 프레임워크 교체를 기본 해법으로 삼지 않습니다.

## 검증과 반환

기존 lint, 타입 검사, 테스트와 빌드 명령을 확인하고 변경 범위에 맞게 실행합니다. 사용자 조작과 실패 상태는 관련 UI 테스트나 실제 브라우저에서 확인합니다. 실행하지 못한 조작은 기대 결과와 함께 미확인으로 남깁니다. 빌드 성공을 사용자 흐름이나 접근성 검증 완료로 보고하지 않습니다.

구현 또는 발견 사항, 실제 확인 범위, 남은 한계를 반환합니다. 성능 개선은 측정 근거가 있을 때만 주장합니다. 검증 결과는 별도 작업 보고에 남기고 AGENTS.md에는 기록하지 않습니다.
