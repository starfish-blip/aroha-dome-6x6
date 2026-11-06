import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: '.',
  testMatch: ['dome_ubo.spec.mjs'],
  timeout: 30000,
  use: {
    baseURL: 'http://localhost:8080',
    headless: true,
    launchOptions: {
      args: ['--use-gl=angle', '--enable-webgl', '--ignore-gpu-blocklist']
    }
  }
});
