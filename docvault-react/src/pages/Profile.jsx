import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import C from '../styles/tokens'
import { useAuth, isAdmin } from '../context/AuthContext'
import api from '../api'
import { Btn, Badge } from '../components/primitives'
import { Input, Field, Alert } from '../components/forms'
import { Card, CardHeader, Page, PageHead, Modal } from '../components/layout'

export default function Profile() {
  const { user, patch, logout } = useAuth()
  const navigate = useNavigate()
  const adm = isAdmin(user)

  const [form, setForm] = useState({
    first_name: user?.first_name || '',
    last_name:  user?.last_name  || '',
    email:      user?.email      || '',
    phone:      user?.phone      || '',
  })
  const [avatarFile, setAvatarFile] = useState(null)
  const [msg,        setMsg]        = useState(null)
  const [loading,    setLoading]    = useState(false)
  const [deleteOpen, setDeleteOpen] = useState(false)
  const [deleting,   setDeleting]   = useState(false)

  const set = k => e => setForm(f => ({ ...f, [k]: e.target.value }))

  const save = async e => {
    e.preventDefault(); setLoading(true); setMsg(null)
    try {
      const fd = new FormData()
      Object.entries(form).forEach(([k, v]) => fd.append(k, v))
      if (avatarFile) fd.append('avatar', avatarFile)
      const d = await api.updateMe(fd)
      patch(d)
      setMsg({ type: 'success', text: 'Profil mis a jour.' })
    } catch { setMsg({ type: 'error', text: 'Une erreur est survenue.' }) }
    finally { setLoading(false) }
  }

  const handleDelete = async () => {
    setDeleting(true)
    try { await api.deleteMe(); await logout(); navigate('/login') }
    catch { setDeleting(false); setDeleteOpen(false) }
  }

  return (
    <Page>
      <PageHead title="Mon Profil" sub="Gerez vos informations personnelles"/>

      <div style={{ display: 'grid', gridTemplateColumns: '260px 1fr', gap: 20, alignItems: 'start' }}>
        {/* Sidebar */}
        <Card style={{ padding: '1.5rem', textAlign: 'center' }}>
          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '1rem' }}>
            <div style={{ width: 82, height: 82, borderRadius: '50%', background: adm ? C.adm : C.ink, color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: C.font, fontSize: '1.6rem', fontWeight: 700, overflow: 'hidden', border: `2px solid ${C.line}` }}>
              {user?.avatar
                ? <img src={user.avatar} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }}/>
                : (user?.username?.[0] || '?').toUpperCase()}
            </div>
          </div>
          <div style={{ fontFamily: C.font, fontSize: '1.1rem', fontWeight: 700 }}>
            {user?.first_name && user?.last_name ? `${user.first_name} ${user.last_name}` : user?.username}
          </div>
          <p style={{ color: C.ink2, fontSize: '.8rem', margin: '3px 0 10px' }}>@{user?.username}</p>
          <Badge status={adm ? 'admin' : 'user'}>{adm ? 'Administrateur' : 'Utilisateur'}</Badge>
          <hr style={{ border: 'none', borderTop: `1px solid ${C.line}`, margin: '1rem 0' }}/>
          <div style={{ fontSize: '.78rem', color: C.ink2, textAlign: 'left', display: 'flex', flexDirection: 'column', gap: 4 }}>
            {form.email && <span>{form.email}</span>}
            {form.phone && <span>{form.phone}</span>}
          </div>
          <div style={{ marginTop: '1.1rem', display: 'flex', flexDirection: 'column', gap: 6 }}>
            <Btn variant="accent"  size="sm" style={{ justifyContent: 'center', width: '100%' }} onClick={() => navigate('/upload')}>Uploader des documents</Btn>
            <Btn variant="outline" size="sm" style={{ justifyContent: 'center', width: '100%' }} onClick={() => navigate('/documents')}>Mes documents</Btn>
          </div>
        </Card>

        {/* Form */}
        <div>
          <Card>
            <CardHeader title="Modifier le profil"/>
            <div style={{ padding: '1.5rem' }}>
              {msg && <Alert type={msg.type} onClose={() => setMsg(null)}>{msg.text}</Alert>}
              <form onSubmit={save}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                  <Input label="Prenom" value={form.first_name} onChange={set('first_name')}/>
                  <Input label="Nom"    value={form.last_name}  onChange={set('last_name')}/>
                </div>
                <Input    label="Email2"     type="email" value={form.email} onChange={set('email')}/>
                <Input    label="Telephone" value={form.phone}  onChange={set('phone')} placeholder="+33 6 00 00 00 00"/>
                <Field label="Photo de profil">
                  <input type="file" accept="image/*" onChange={e => setAvatarFile(e.target.files[0])} style={{ fontSize: '.85rem', color: C.ink }}/>
                </Field>
                <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                  <Btn type="submit" variant="primary" loading={loading}>Enregistrer les modifications</Btn>
                </div>
              </form>
            </div>
          </Card>
        </div>
      </div>

    </Page>
  )
}
