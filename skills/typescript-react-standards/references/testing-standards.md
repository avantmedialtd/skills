# Testing Standards

## Philosophy

Tests exist to give you confidence to ship. If your tests don't catch real bugs or they break on every refactor, they're not doing their job.

## Test Types and When to Use Them

### Unit Tests (Vitest)

Test pure functions, utilities, and custom hooks in isolation. These should be fast, deterministic, and numerous.

```typescript
// utils/formatCurrency.test.ts
import { formatCurrency } from './formatCurrency';

describe('formatCurrency', () => {
    it('formats GBP correctly', () => {
        expect(formatCurrency(1234.5, 'GBP')).toBe('£1,234.50');
    });

    it('handles zero', () => {
        expect(formatCurrency(0, 'GBP')).toBe('£0.00');
    });

    it('handles negative amounts', () => {
        expect(formatCurrency(-50, 'GBP')).toBe('-£50.00');
    });
});
```

For hooks, use `@testing-library/react-hooks` (or `renderHook` from Testing Library):

```typescript
import { renderHook, act } from '@testing-library/react';
import { useToggle } from './useToggle';

it('toggles value', () => {
    const { result } = renderHook(() => useToggle(false));
    expect(result.current[0]).toBe(false);
    act(() => result.current[1]());
    expect(result.current[0]).toBe(true);
});
```

### Component Tests (Testing Library)

Render components, interact with them as a user would, and assert on visible output. Never test internal state or implementation details.

```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Counter } from './Counter';

it('increments count on click', async () => {
  render(<Counter initialCount={0} />);
  await userEvent.click(screen.getByRole('button', { name: /increment/i }));
  expect(screen.getByText('Count: 1')).toBeInTheDocument();
});
```

Rules:

- Query by role, label, or text — never by test ID unless there's no semantic alternative
- Use `userEvent` over `fireEvent` — it simulates real user interactions
- Don't test CSS classes or DOM structure — test what the user sees and does

### Integration Tests

Test real integrations: API routes hitting a test database, service layers calling real dependencies. Use test containers or in-memory databases where practical.

```typescript
// api/users.integration.test.ts
import { createTestApp } from '../test/helpers';

describe('POST /api/users', () => {
    it('creates a user and returns 201', async () => {
        const app = await createTestApp();
        const response = await app.inject({
            method: 'POST',
            url: '/api/users',
            payload: { email: 'test@example.com', name: 'Test User' },
        });
        expect(response.statusCode).toBe(201);
        expect(response.json()).toMatchObject({ email: 'test@example.com' });
    });
});
```

### E2E Tests (Playwright)

Reserve for critical user journeys. These are slow and flaky by nature — keep the suite small and focused.

```typescript
// e2e/auth.spec.ts
import { test, expect } from '@playwright/test';

test('user can sign in and see dashboard', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel('Email').fill('user@example.com');
    await page.getByLabel('Password').fill('password');
    await page.getByRole('button', { name: 'Sign in' }).click();
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
});
```

## Mocking Guidelines

Mock at the boundary, not in the middle. The goal is to test real code, not verify your mock setup.

**Good boundaries to mock:**

- HTTP clients (MSW for API mocking)
- Time (`vi.useFakeTimers()`)
- External services (payment gateways, email providers)

**Bad things to mock:**

- Your own modules (if you're mocking `UserService` to test `UserController`, test them together)
- Database queries (use a test database instead)
- React components (if you're mocking a child component, your test is too granular)

```typescript
// Good: MSW handler for external API
import { http, HttpResponse } from 'msw';

const handlers = [
    http.get('/api/users', () => {
        return HttpResponse.json([
            { id: '1', name: 'Alice' },
            { id: '2', name: 'Bob' },
        ]);
    }),
];
```

## Test Organisation

Co-locate tests with the code they test:

```
Button/
├── Button.tsx
├── Button.test.tsx    # Component test
utils/
├── formatCurrency.ts
├── formatCurrency.test.ts  # Unit test
```

E2E tests live in a top-level `e2e/` directory.

## Coverage

Don't chase percentages. A codebase with 60% meaningful coverage beats 95% coverage that mostly tests getters and mocks.

Focus coverage on:

- Business logic and data transformations
- Complex conditional flows
- Error handling paths
- User-facing interactions

Skip coverage on:

- Type definitions
- Configuration files
- Trivial pass-through functions
- Generated code
