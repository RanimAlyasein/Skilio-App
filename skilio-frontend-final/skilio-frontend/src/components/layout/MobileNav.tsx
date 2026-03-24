import { NavLink } from 'react-router-dom'
const NAV = [
  { to: '/dashboard', label: 'Home',     icon: '⬡', end: true },
  { to: '/children',  label: 'Children', icon: '◎' },
  { to: '/learn',     label: 'Worlds',   icon: '◈' },
]
export function MobileNav() {
  return (
    <nav className="mob-nav" style={{ display: 'grid' }}>
      {NAV.map(item => (
        <NavLink key={item.to} to={item.to} end={item.end} className={({ isActive }) => `mob-btn${isActive ? ' on' : ''}`}>
          <span className="mob-ic">{item.icon}</span>
          <span className="mob-lb">{item.label}</span>
        </NavLink>
      ))}
    </nav>
  )
}
