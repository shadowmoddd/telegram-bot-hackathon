import { useLocation, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'

interface NavItem {
  path: string
  icon: string
  label: string
}

const navItems: NavItem[] = [
  { path: '/', icon: '🏠', label: 'Главная' },
  { path: '/tree', icon: '🗺', label: 'Маршрут' },
  { path: '/achievements', icon: '🏆', label: 'Успехи' },
  { path: '/profile', icon: '👤', label: 'Профиль' },
]

export default function BottomNav() {
  const location = useLocation()
  const navigate = useNavigate()

  return (
    <nav style={{
      position: 'fixed',
      bottom: 0,
      left: 0,
      right: 0,
      height: '72px',
      background: 'rgba(11, 15, 46, 0.92)',
      backdropFilter: 'blur(20px)',
      WebkitBackdropFilter: 'blur(20px)',
      borderTop: '1px solid var(--border)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-around',
      padding: '0 8px',
      zIndex: 100,
      boxShadow: '0 -4px 24px rgba(0,0,0,0.3)'
    }}>
      {navItems.map((item) => {
        const isActive = location.pathname === item.path

        return (
          <motion.button
            key={item.path}
            onClick={() => navigate(item.path)}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '4px',
              padding: '8px 16px',
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              position: 'relative',
              flex: 1
            }}
            whileTap={{ scale: 0.92 }}
          >
            <motion.span
              style={{
                fontSize: '22px',
                lineHeight: 1,
                filter: isActive ? 'drop-shadow(0 0 8px rgba(124,58,237,0.8))' : 'none',
                transition: 'filter 0.25s'
              }}
              animate={{ scale: isActive ? 1.1 : 1 }}
              transition={{ type: 'spring', stiffness: 400, damping: 20 }}
            >
              {item.icon}
            </motion.span>
            <span style={{
              fontSize: '10px',
              fontWeight: isActive ? 600 : 400,
              color: isActive ? 'transparent' : 'var(--text-muted)',
              background: isActive ? 'var(--grad-primary)' : 'none',
              WebkitBackgroundClip: isActive ? 'text' : 'unset',
              backgroundClip: isActive ? 'text' : 'unset',
              WebkitTextFillColor: isActive ? 'transparent' : 'inherit',
              transition: 'color 0.25s',
              lineHeight: 1
            }}>
              {item.label}
            </span>
            <AnimatePresence>
              {isActive && (
                <motion.div
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0, opacity: 0 }}
                  transition={{ type: 'spring', stiffness: 500, damping: 25 }}
                  style={{
                    position: 'absolute',
                    bottom: '-2px',
                    width: '4px',
                    height: '4px',
                    borderRadius: '50%',
                    background: 'var(--grad-primary)',
                    boxShadow: '0 0 8px rgba(124,58,237,0.8)'
                  }}
                />
              )}
            </AnimatePresence>
          </motion.button>
        )
      })}
    </nav>
  )
}
