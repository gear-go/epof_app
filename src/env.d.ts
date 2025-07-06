/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_ANTHROPIC_API_KEY: string
  readonly VITE_APP_TITLE: string
  readonly VITE_DEPLOYMENT_ENV: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
