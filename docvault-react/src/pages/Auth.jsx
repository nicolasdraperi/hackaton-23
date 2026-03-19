import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import C from '../styles/tokens'
import { useAuth, isAdmin } from '../context/AuthContext'
import api from '../api'
import { Btn } from '../components/primitives'
import { Input, Alert } from '../components/forms'

function AuthWrap({ tab, maxWidth = 400, children }) {
  const navigate = useNavigate()
  return (
    <div style={{ minHeight: '100vh', background: C.smoke, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem 1rem' }}>
      <div style={{ width: '100%', maxWidth }}>
        <div style={{ textAlign: 'center', marginBottom: '1.75rem' }}>
          <h1 style={{ fontFamily: C.font, fontWeight: 800, fontSize: '1.9rem', letterSpacing: '-.03em' }}>
            Doc<span style={{ color: C.acc }}>Vault</span>
          </h1>
          <p style={{ color: C.ink2, fontSize: '.875rem', marginTop: 4 }}>Gestion des documents</p>
        </div>
        <div style={{ background: '#fff', border: `1px solid ${C.line}`, borderRadius: C.r, boxShadow: C.shadow, padding: '1.75rem' }}>
          <div style={{ display: 'flex', borderBottom: `2px solid ${C.line}`, marginBottom: '1.5rem' }}>
            {[['Connexion', 'login'], ['Creer un compte', 'register']].map(([lbl, t]) => (
              <span key={t} onClick={() => navigate('/' + t)}
                style={{
                  flex: 1, textAlign: 'center', padding: '10px', fontSize: '.875rem',
                  fontWeight: 600, cursor: 'pointer',
                  color: tab === t ? C.ink : C.ink2,
                  borderBottom: `2px solid ${tab === t ? C.ink : 'transparent'}`,
                  marginBottom: -2, transition: 'all .12s',
                }}>
                {lbl}
              </span>
            ))}
          </div>
          {children}
        </div>
      </div>
    </div>
  )
}

export function Login() {
  const { login } = useAuth()
  const navigate  = useNavigate()
  const [form, setForm] = useState({ username: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const set = k => e => setForm(f => ({ ...f, [k]: e.target.value }))

  const submit = async e => {
    e.preventDefault(); setError(''); setLoading(true)
    try {
      const user = await login(form.username, form.password)
      navigate(isAdmin(user) ? '/admin' : '/documents')
    } catch {
      setError('Identifiants incorrects, veuillez reessayer.')
    } finally { setLoading(false) }
  }

  return (
    <AuthWrap tab="login">
      {error && <Alert type="error" onClose={() => setError('')}>{error}</Alert>}
      <form onSubmit={submit}>
        <Input label="Nom d'utilisateur" value={form.username} onChange={set('username')} placeholder="votre_username" required autoFocus/>
        <Input label="Mot de passe" type="password" value={form.password} onChange={set('password')} placeholder="••••••••" required/>
        <Btn type="submit" variant="primary" loading={loading} style={{ width: '100%', justifyContent: 'center', marginTop: 4 }}>
          Se connecter
        </Btn>
      </form>
    </AuthWrap>
  )
}

export function Register() {
  const { setUser } = useAuth()
  const navigate    = useNavigate()
  const [form, setForm] = useState({ username: '', first_name: '', last_name: '', email: '', password1: '', password2: '' })
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)
  const set = k => e => setForm(f => ({ ...f, [k]: e.target.value }))

  const submit = async e => {
    e.preventDefault(); setErrors({}); setLoading(true)
    try {
      const d = await api.register(form)
      setUser(d.user)
      navigate('/documents')
    } catch (ex) {
      setErrors(ex.data || { non_field_errors: ['Une erreur est survenue.'] })
    } finally { setLoading(false) }
  }

  return (
    <AuthWrap tab="register" maxWidth={460}>
      {errors.non_field_errors && <Alert type="error">{errors.non_field_errors.join(' ')}</Alert>}
      <form onSubmit={submit}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
          <Input label="Prenom" value={form.first_name} onChange={set('first_name')} error={errors.first_name?.[0]}/>
          <Input label="Nom"    value={form.last_name}  onChange={set('last_name')}  error={errors.last_name?.[0]}/>
        </div>
        <Input label="Nom d'utilisateur" value={form.username}  onChange={set('username')}  error={errors.username?.[0]}  required autoFocus/>
        <Input label="Email" type="email" value={form.email}    onChange={set('email')}    error={errors.email?.[0]}/>
        <Input label="Mot de passe"              type="password" value={form.password1} onChange={set('password1')} error={errors.password1?.[0]} required/>
        <Input label="Confirmer le mot de passe" type="password" value={form.password2} onChange={set('password2')} error={errors.password2?.[0]} required/>
        <Btn type="submit" variant="accent" loading={loading} style={{ width: '100%', justifyContent: 'center', marginTop: 4 }}>
          Creer mon compte
        </Btn>
      </form>
    </AuthWrap>
  )
}
