import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Nav from './components/Nav'
import { RequireAuth, RequireAdmin, Root } from './components/Guards'

import { Login, Register }                                      from './pages/Auth'
import Profile                                                  from './pages/Profile'
import { Upload, MyDocuments }                                  from './pages/Documents'
import { AdminDashboard, AdminReview, AdminUpload, AdminUsers } from './pages/Admin'

export default function App() {
  const { user } = useAuth()
  return (
    <>
      {user && <Nav/>}
      <Routes>
        <Route path="/login"    element={<Login/>}/>
        <Route path="/register" element={<Register/>}/>
        <Route path="/"         element={<Root/>}/>

        <Route path="/profile"   element={<RequireAuth><Profile/></RequireAuth>}/>
        <Route path="/upload"    element={<RequireAuth><Upload/></RequireAuth>}/>
        <Route path="/documents" element={<RequireAuth><MyDocuments/></RequireAuth>}/>

        <Route path="/admin"        element={<RequireAuth><RequireAdmin><AdminDashboard/></RequireAdmin></RequireAuth>}/>
        <Route path="/admin/review" element={<RequireAuth><RequireAdmin><AdminReview/></RequireAdmin></RequireAuth>}/>
        <Route path="/admin/upload" element={<RequireAuth><RequireAdmin><AdminUpload/></RequireAdmin></RequireAuth>}/>
        <Route path="/admin/users"  element={<RequireAuth><RequireAdmin><AdminUsers/></RequireAdmin></RequireAuth>}/>

        <Route path="*" element={<Navigate to="/" replace/>}/>
      </Routes>
    </>
  )
}
