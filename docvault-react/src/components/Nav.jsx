import { NavLink, useNavigate } from 'react-router-dom'
import C from '../styles/tokens'
import { useAuth, isAdmin } from '../context/AuthContext'
import { Ava } from './layout'

const linkStyle = ({ isActive }) => ({
  color:      isActive ? '#fff' : 'rgba(255,255,255,.6)',
  background: isActive ? 'rgba(255,255,255,.12)' : 'transparent',
  padding: '6px 11px', borderRadius: 5, fontSize: '.82rem',
  fontWeight: isActive ? 500 : 400, transition: 'all .12s', whiteSpace: 'nowrap',
})

export default function Nav() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const adm = isAdmin(user)

  const handleLogout = async () => { await logout(); navigate('/login') }

  return (
    <nav style={{
      background:   adm ? '#160e35' : C.ink,
      borderBottom: adm ? `2px solid ${C.adm}` : 'none',
      height: 56, padding: '0 24px',
      display: 'flex', alignItems: 'center', gap: 10,
      position: 'sticky', top: 0, zIndex: 100,
    }}>
      {/* Brand */}
      <NavLink to="/" style={{ fontFamily: C.font, fontWeight: 800, fontSize: '1.1rem', color: '#fff', letterSpacing: '-.02em', flexShrink: 0 }}>
        Deus<span style={{ color: C.acc }}>Vult</span>
        {adm && (
          <span style={{ background: C.adm, color: '#fff', fontSize: '.65rem', padding: '2px 6px', borderRadius: 4, fontWeight: 600, marginLeft: 8, letterSpacing: '.04em', verticalAlign: 'middle' }}>
            ADMIN
          </span>
        )}
      </NavLink>

      {/* Links */}
      <div style={{ display: 'flex', gap: 2, marginLeft: 'auto', alignItems: 'center', flexWrap: 'wrap' }}>
        {adm ? (
          <>
            <NavLink to="/admin"        end style={linkStyle}>Tableau de bord</NavLink>
            <NavLink to="/admin/review"     style={linkStyle}>Revision</NavLink>
            <NavLink to="/admin/upload"     style={linkStyle}>Upload</NavLink>
            <NavLink to="/admin/users"      style={linkStyle}>Utilisateurs</NavLink>
            <NavLink to="/profile"          style={linkStyle}>Profil</NavLink>
          </>
        ) : (
          <>
            <NavLink to="/profile"          style={linkStyle}>Profil</NavLink>
            <NavLink to="/upload"           style={linkStyle}>Upload</NavLink>
            <NavLink to="/documents"        style={linkStyle}>Mes documents</NavLink>
          </>
        )}

        <span style={{ width: 1, height: 18, background: 'rgba(255,255,255,.12)', margin: '0 4px' }}/>

        <div style={{ display: 'flex', alignItems: 'center', gap: 7, color: 'rgba(255,255,255,.85)', fontSize: '.82rem' }}>
          <Ava user={user} size={28}/>
          <span>{user?.username}</span>
        </div>

        <button
          onClick={handleLogout}
          style={{ color: 'rgba(255,255,255,.6)', background: 'none', border: 'none', padding: '6px 11px', borderRadius: 5, fontSize: '.82rem', cursor: 'pointer', transition: 'all .12s' }}
          onMouseEnter={e => { e.target.style.background = 'rgba(255,255,255,.09)'; e.target.style.color = '#fff' }}
          onMouseLeave={e => { e.target.style.background = 'none'; e.target.style.color = 'rgba(255,255,255,.6)' }}>
          Deconnexion
        </button>
      </div>
    </nav>
  )
}
