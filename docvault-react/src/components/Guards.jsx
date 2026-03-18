import { Navigate, useLocation } from 'react-router-dom'
import { useAuth, isAdmin } from '../context/AuthContext'
import { Spinner } from '../components/primitives'

function FullPageSpinner() {
  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
      <Spinner size={32}/>
    </div>
  )
}

export function RequireAuth({ children }) {
  const { user, ready } = useAuth()
  const location = useLocation()
  if (!ready) return <FullPageSpinner/>
  return user ? children : <Navigate to="/login" state={{ from: location }} replace/>
}

export function RequireAdmin({ children }) {
  const { user } = useAuth()
  return isAdmin(user) ? children : <Navigate to="/documents" replace/>
}

export function Root() {
  const { user, ready } = useAuth()
  if (!ready) return <FullPageSpinner/>
  return <Navigate to={user ? (isAdmin(user) ? '/admin' : '/documents') : '/login'} replace/>
}
