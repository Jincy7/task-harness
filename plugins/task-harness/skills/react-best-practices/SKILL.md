---
name: react-best-practices
description: Use when writing or reviewing React code involving request waterfalls, bundle size, state ownership, Effects, rendering performance, asynchronous UI, accessibility, tests, or server/client boundaries.
license: MIT
---

# React Best Practices

React 화면의 데이터 흐름, 상태, 렌더링과 사용자 조작을 검토하고 요청한 범위에서 개선합니다. Vercel 지침의 핵심을 Python 스킬과 같은 짧은 진입점 및 네 가지 상세 참조로 축약했습니다. 각 참조는 적용 조건, 코드 예제와 체크리스트를 포함합니다.

## How To Use This Skill

먼저 React 버전, 프레임워크와 라우터, SSR 여부, Compiler 및 기존 검사 설정을 확인합니다. 현재 변경이 지나는 경계의 문서만 읽습니다.

- 요청 순서, 캐시 소유권, 오래된 응답과 로딩은 [Data Fetching](references/data-fetching.md)을 읽습니다.
- 상태 소유권, Effect, key와 측정에 근거한 최적화는 [Rendering and State](references/rendering-and-state.md)를 읽습니다.
- 서버 인증, 요청별 상태, DTO와 지연 로딩은 [Server and Bundle](references/server-and-bundle.md)을 읽습니다.
- 폼, 실패, 접근성, hydration과 실제 동작 검증은 [Testing and Boundaries](references/testing-and-boundaries.md)를 읽습니다.

검색 변경은 데이터 요청과 상태, 저장 변경은 서버 경계와 UI 검증처럼 필요한 참조를 함께 사용합니다. Next.js와 Server Components 지침은 해당 환경에서만 적용합니다. 일반 SPA에 Next.js나 서버 캐시를 도입하지 않습니다.

## Review Focus

- 오류, 권한과 사용자 데이터 보존을 먼저 확인합니다.
- 독립 요청의 순차 실행과 불필요한 초기 번들을 확인합니다.
- 파생 상태, 잘못된 key와 Effect 의존성 및 정리를 확인합니다.
- 서버 입력, 요청별 사용자 상태, 캐시 범위와 클라이언트 전달 필드를 확인합니다.
- 성능은 측정 후 개선하며 memo, 캐시와 전환 API를 일괄 적용하지 않습니다.

검토 요청이면 위치, 재현 조작, 사용자 영향과 수정 방향을 반환하고 파일은 수정하지 않습니다. 구현 요청이면 기존 데이터 계층과 컴포넌트 구조에 맞춰 수정하고 검증합니다. 새 상태 관리 라이브러리, 프레임워크나 테스트 도구 도입을 기본 해법으로 삼지 않습니다.

참조 전체를 답변에 복제하지 않습니다. 기존 lint, 타입 검사, 테스트와 빌드를 변경 범위에 맞게 실행합니다. 빌드 성공을 UI, 접근성 또는 저장 검증 완료로 보고하지 않습니다. 실제 실행 결과, 성능 측정 조건과 미확인을 구분하고 별도 작업 보고에 기록합니다. AGENTS.md에는 구현 현황을 추가하지 않습니다.

## Reference Map

| 관심사 | 상세 지침 |
| --- | --- |
| 독립 요청, 캐시, 경쟁 상태와 스트리밍 | [data-fetching.md](references/data-fetching.md) |
| 상태, Effect, identity와 렌더링 비용 | [rendering-and-state.md](references/rendering-and-state.md) |
| 서버 권한, 요청 격리, DTO와 번들 | [server-and-bundle.md](references/server-and-bundle.md) |
| 사용자 조작, 실패, 접근성과 검증 근거 | [testing-and-boundaries.md](references/testing-and-boundaries.md) |

## Attribution

Vercel의 MIT 지침을 선별하고 Task Harness의 동작 검증 지침을 더했습니다. 출처, 고정 리비전과 선별 범위는 [NOTICE](NOTICE), 라이선스 전문은 [LICENSE](LICENSE)에 있습니다.
