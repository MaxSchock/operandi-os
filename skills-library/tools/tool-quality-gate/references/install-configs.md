# Quality Gate — Installation Configs Reference

Read this file during SETUP mode to get the exact packages, config files, and templates per stack.

## Table of Contents
1. [Packages by stack](#packages)
2. [Vitest config](#vitest-config)
3. [Husky hooks](#husky-hooks)
4. [Package.json scripts](#scripts)
5. [API route test template](#api-test-template)
6. [Page render test template](#page-test-template)

---

## Packages

### Next.js (App Router) + Supabase
```bash
npm install -D vitest @vitejs/plugin-react @testing-library/react @testing-library/jest-dom jsdom
npm install -D @playwright/test
npm install -D husky lint-staged
npx playwright install chromium
npx husky init
```

### Next.js (App Router) solo
Same as above minus Supabase-specific mocks.

### React (Vite)
```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom
npm install -D husky lint-staged
npx husky init
```

### Node.js API (no frontend)
```bash
npm install -D vitest
npm install -D husky lint-staged
npx husky init
```

---

## Vitest Config

### vitest.config.ts (Next.js)
```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./vitest.setup.ts'],
    include: ['**/*.test.{ts,tsx}', '**/*.spec.{ts,tsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json-summary'],
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

### vitest.setup.ts
```typescript
import '@testing-library/jest-dom/vitest'
```

### vitest.config.ts (Node.js API only)
```typescript
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    include: ['**/*.test.ts', '**/*.spec.ts'],
  },
})
```

---

## Husky Hooks

### .husky/pre-commit
```bash
npx lint-staged
npx vitest run --reporter=verbose 2>&1 | tail -20
```

### .husky/pre-push
```bash
echo "🔍 Quality Gate pre-push check..."
npm run build 2>&1 | tail -5
if [ $? -ne 0 ]; then
  echo "🔴 BUILD FALLO — No se puede hacer push. Arregla los errores de build primero."
  exit 1
fi
npx vitest run 2>&1 | tail -10
if [ $? -ne 0 ]; then
  echo "🔴 TESTS FALLARON — Arregla los tests antes de hacer push."
  exit 1
fi
echo "🟢 Quality Gate: Todo OK. Push permitido."
```

---

## Scripts

Add to package.json:
```json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage",
    "test:e2e": "playwright test",
    "quality-check": "npm run build && vitest run && echo '✅ Quality Gate: PASSED'"
  },
  "lint-staged": {
    "*.{ts,tsx}": ["eslint --fix", "prettier --write"]
  }
}
```

---

## API Test Template

For each API route file (`app/api/**/route.ts`), create a sibling `route.test.ts`:

```typescript
import { describe, it, expect, vi } from 'vitest'
import { GET, POST } from './route'
import { NextRequest } from 'next/server'

describe('API: /api/[ROUTE_NAME]', () => {
  // 1. Happy path
  it('should return 200 with valid request', async () => {
    const req = new NextRequest('http://localhost/api/[ROUTE_NAME]')
    const res = await GET(req)
    expect(res.status).toBe(200)
  })

  // 2. Invalid data
  it('should return 400 with invalid data', async () => {
    const req = new NextRequest('http://localhost/api/[ROUTE_NAME]', {
      method: 'POST',
      body: JSON.stringify({}),
    })
    const res = await POST(req)
    expect(res.status).toBe(400)
  })

  // 3. No auth (only if route uses auth)
  it('should return 401 without auth token', async () => {
    const req = new NextRequest('http://localhost/api/[ROUTE_NAME]')
    // Don't set Authorization header
    const res = await GET(req)
    expect(res.status).toBe(401)
  })

  // 4. Insufficient permissions (only if route uses roles)
  it('should return 403 with insufficient permissions', async () => {
    const req = new NextRequest('http://localhost/api/[ROUTE_NAME]', {
      headers: { Authorization: 'Bearer test-token-no-admin' },
    })
    const res = await GET(req)
    expect(res.status).toBe(403)
  })

  // 5. Not found
  it('should return 404 for non-existent resource', async () => {
    const req = new NextRequest('http://localhost/api/[ROUTE_NAME]/nonexistent-id')
    const res = await GET(req)
    expect(res.status).toBe(404)
  })

  // 6. Server error (mock DB failure)
  it('should handle server errors gracefully', async () => {
    // Mock the database to throw
    vi.mock('@/lib/supabase', () => ({
      createClient: () => ({
        from: () => ({ select: () => { throw new Error('DB down') } }),
      }),
    }))
    const req = new NextRequest('http://localhost/api/[ROUTE_NAME]')
    const res = await GET(req)
    expect(res.status).toBe(500)
  })
})
```

Adapt the template based on what the route actually exports (GET, POST, PUT, DELETE, PATCH).
Skip auth tests (401/403) if the route doesn't import auth utilities.

---

## Page Test Template

For each page (`app/**/page.tsx`), create a sibling `page.test.tsx`:

```typescript
import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import Page from './page'

describe('Page: /[ROUTE_PATH]', () => {
  it('should render without crashing', () => {
    const { container } = render(<Page />)
    expect(container.innerHTML).not.toBe('')
  })
})
```

For Server Components that use async data fetching, test the component with mocked data:
```typescript
import { describe, it, expect, vi } from 'vitest'

// Mock the data fetching
vi.mock('@/lib/data', () => ({
  fetchItems: vi.fn().mockResolvedValue([{ id: 1, name: 'Test' }]),
}))

// Then render and test
```
