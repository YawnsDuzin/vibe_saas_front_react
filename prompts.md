=========================================
2025.12.25(목)
=========================================

[opus]
변경된 코드에 맞게 문서 업데이트할 부분있으면 모두 업데이트해줘.

=========================================

## Error Type
Build Error

## Error Message
Module not found: Can't resolve '@/lib/api'

## Build Output
./src/stores/authStore.ts:4:1
Module not found: Can't resolve '@/lib/api'
  2 | import { persist } from 'zustand/middleware';
  3 | import type { User } from '@/types';
> 4 | import { authApi, clearTokens, getAccessToken } from '@/lib/api';
    | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  5 |
  6 | interface AuthState {
  7 |   user: User | null;

Import map: aliased to relative './src/lib/api' inside of [project]/

Import traces:
  Client Component Browser:
    ./src/stores/authStore.ts [Client Component Browser]
    ./src/app/page.tsx [Client Component Browser]
    ./src/app/page.tsx [Server Component]

  Client Component SSR:
    ./src/stores/authStore.ts [Client Component SSR]
    ./src/app/page.tsx [Client Component SSR]
    ./src/app/page.tsx [Server Component]

https://nextjs.org/docs/messages/module-not-found

Next.js version: 16.1.1 (Turbopack)

[추가프롬프트]
지금 새로 생성하는게 누락되어 있었던 것이 확실한거지?? 혹시 다른 중복코드가 있는건 아닌지 확인을 한후, 진행을 해줘.

=========================================

/init
/clear

=========================================



=========================================
=========================================
=========================================
=========================================
=========================================
=========================================