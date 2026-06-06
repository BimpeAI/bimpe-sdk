import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    include: ['tests/unit/**/*.test.ts', 'tests/integration/**/*.test.ts'],
    exclude: ['tests/smoke/**', 'tests/live/**'],
    environment: 'node',
    globals: false,
    passWithNoTests: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov'],
      include: ['src/**/*.ts'],
      exclude: ['src/**/index.ts', 'src/version.ts'],
      thresholds: {
        'src/core/**/*.ts': { statements: 95, branches: 95, functions: 95, lines: 95 },
        'src/resources/**/*.ts': { statements: 85, branches: 85, functions: 85, lines: 85 },
      },
    },
  },
});
