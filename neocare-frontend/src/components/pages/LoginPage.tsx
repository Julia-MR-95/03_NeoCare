import { useState, useEffect, type SubmitEvent} from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

export default function LoginPage() {
    const {login, user, loading} = useAuth()
    const navigate = useNavigate()
    const [searchParams] = useSearchParams() 
    //es el lector de React Router para los parámetros que van después de ? en la URL
    //tras el login, primero comprueba si hay redirect antes de mandar a '/'
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState<string | null>(null)
    const [submitting, setSubmitting] = useState(false)

    //comprobación de q hay una sesión validada
    useEffect(() => {
        if (!loading && user) {
            const redirect = searchParams.get('redirect')
            navigate(redirect || '/', {replace: true})
        }
    }, [loading, user, searchParams, navigate])

    const handleSubmit = async (e: SubmitEvent) => {
        e.preventDefault()
        setError(null)
        setSubmitting(true)
        try {
            await login(email, password)
            const redirect = searchParams.get('redirect')
            navigate(redirect || '/')
        } catch {
            setError('Email o contraseña incorrecto.')
        } finally {
            setSubmitting(false)
        }
    }

    //check de user iniciado
    if (loading || user) return null

    return (
        <div style={{display:'flex', minHeight: '100vh', alignItems: 'center', justifyContent: 'center', background: '#f3f4f6' }}>
            <form
            onSubmit={handleSubmit}
            style={{ background: 'gray', padding: '2rem', borderRadius: '10px', width: '320px', boxShadow: '0 1px 3px rgba(0,0,0,0,1)'}}>
                <h1 style={{ fontSize: '20px', marginBottom: '1.5rem' }}>Iniciar sesión</h1>
                
                <label style={{ display: 'block', fontSize: '13px', marginBottom: '4px'}}>Email</label>
                <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                style={{ width: '100%', padding: '8px', marginBottom: '1rem', border: '1px solid #d1d5db', borderRadius: '6px' }} />

                <label style={{ display: 'block', fontSize: '13px', marginBottom: '4px' }}>Contraseña</label>
                <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                style={{ width: '100%', padding: '8px', marginBottom: '1rem', border: '1px solid #d1d5db', borderRadius: '6px'}} />

                {error && <p style={{ color: '#dc2626', fontSize: '13px', marginBottom: '1rem'}}>{error}</p>}

                <button
                type="submit"
                disabled={submitting}
                style={{ width: '100%', padding: '10px', background: '#2563eb', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }} >
                    {submitting ? 'Entrando...' : 'Entrar'}
                </button>
            </form>
        </div>
    )
}