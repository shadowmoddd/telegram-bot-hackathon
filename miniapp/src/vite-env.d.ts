/// <reference types="vite/client" />

interface Window {
  Telegram?: {
    WebApp?: {
      openLink: (url: string, options?: { try_instant_view?: boolean }) => void
      initDataUnsafe?: {
        user?: {
          first_name: string
          username?: string
          photo_url?: string
        }
      }
    }
  }
}
