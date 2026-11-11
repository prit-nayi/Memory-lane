import { useEffect, useState } from 'react'

const RECONNECT_MAX_DELAY_MS = 30000

function getWebSocketUrl() {
  const apiOrigin =
    import.meta.env.VITE_API_BASE_URL || window.location.origin
  const url = new URL('/api/v1/slideshow/ws', apiOrigin)
  url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:'
  return url.toString()
}

export default function useSlideshowSocket(onPhotosUpdated) {
  const [connectionState, setConnectionState] = useState('connecting')

  useEffect(() => {
    let active = true
    let retryTimer
    let retryDelay = 1000
    let socket

    function connect() {
      if (!active) {
        return
      }

      setConnectionState('connecting')
      socket = new WebSocket(getWebSocketUrl())

      socket.addEventListener('open', () => {
        if (!active) {
          return
        }
        retryDelay = 1000
        setConnectionState('connected')
        onPhotosUpdated()
      })

      socket.addEventListener('message', (event) => {
        try {
          const message = JSON.parse(event.data)
          if (message.type === 'photos_updated') {
            onPhotosUpdated()
          }
        } catch {
          socket.close(4000, 'Invalid server message')
        }
      })

      socket.addEventListener('close', () => {
        if (!active) {
          return
        }
        setConnectionState('reconnecting')
        retryTimer = window.setTimeout(connect, retryDelay)
        retryDelay = Math.min(retryDelay * 2, RECONNECT_MAX_DELAY_MS)
      })

      socket.addEventListener('error', () => socket.close())
    }

    retryTimer = window.setTimeout(connect, 0)
    return () => {
      active = false
      window.clearTimeout(retryTimer)
      socket?.close()
    }
  }, [onPhotosUpdated])

  return connectionState
}
