//Tablero para ver, editar y eliminar una tarjeta
import { useState, useEffect } from 'react'
import apiClient from '../../api/clients'
import { useAuth } from '../../context/AuthContext'
import type { Card, User } from '../../types'

interface Props {
    card: Card
    listTitle: string
    onClose: () => void
    onUpdated: (card: Card) => void
    onDeleted: (cardId: number) => void
}

//convierte una fecha ISO en el formato YYYY-MM-DD para <input type="date">
const toDateInput = (iso?: string) => (iso ? iso.slice(0,10) : '')



export default function CardDetailModal({ card, listTitle, onClose, onUpdated, onDeleted }: Props) {
    const { user } = useAuth()
    //sólo el creador de la tarjeta puede modificarla o eliminarla
//visible sólo para el creador
    const isOwner = card.creator_id === user?.id


    const [users, setUsers] = useState<User[]>([])
    const [title, setTitle] = useState(card.title)
    const [description, setDescription] = useState(card.description ?? '')
    const [dueDate, setDueDate] = useState(toDateInput(card.due_date))
    const [assigneeId, setAssigneeId ] = useState<string>(card.assignee_id ? String(card.assignee_id): '')
    const [saving, setSaving] = useState(false)
    const [deleting, setDeleting] = useState(false)
    const [error, setError] = useState <string | null>(null)

    useEffect(() => {
        apiClient.get<User[]>('/users/').then((res) => setUsers(res.data)).catch(() => {})
    }, [])

    const findUserEmail = (id?:number) => 
        users.find((u) => u.id === id)?.email ?? (id ? `Usuario #${id}` : null)

    const handleSave = async () => {
        setError(null)
        setSaving(true)
        try {
            const res = await apiClient.put<Card>(`/cards/${card.id}`, {
                title,
                description: description.trim() || null,
                due_date: dueDate ? new Date(dueDate).toISOString() : null,
                assignee_id: assigneeId ? Number(assigneeId) : null,
            })
            onUpdated(res.data)
            onClose()
        } catch {
            setError('No se pudo guardar. Inténtalo de nuevo.')
        } finally {
            setSaving(false)
        }
    }

    const handleDelete = async () => {
        if (!confirm('¿Seguro que quieres eliminar esta tarjeta? No se puede deshacer.')) return
        setDeleting(true)
        try {
            await apiClient.delete(`/cards/${card.id}`)
            onDeleted(card.id)
            onClose()
        } catch {
            setError('No se pudo eliminar la tarjeta.')
            setDeleting(false)
        }
    }

    return (
        <div
        onClick={onClose}
        style={{
            position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000,
            }}
        >
            <div onClick={(e) => e.stopPropagation()}
            style={{
                background: 'white', borderRadius: '10px', padding: '1.5rem',
                width: '420px', maxWidth: '90vw', maxHeight: '85vh', overflowY: 'auto',
                boxShadow: '0 10px 30px rgba(0,0,0,0.2)',
            }}
            >
                <div style={{ display: 'flex',  justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem'}}>
                    <span style ={{fontSize: '11px', color: '#9ca3af', textTransform: 'uppercase'}}>{listTitle}</span>
                    <button onClick={onClose} style= {{background: 'none', border: 'none', fontSize: '18px', cursor: 'pointer', color: '#9ca3af'}}>X</button>
                </div>

                {/* ==TITULO===*/}
                <label style={{ display: 'block', fontSize: '12px', color: '#6b7280', marginBottom: '4px'}}>Título</label>
                <input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                disabled={!isOwner}
                style={{width: '100%', padding: '8px', marginBottom: '12px', borderRadius: '6px', border: '1px solid #d1d5db', fontSize: '14px', fontWeight: 600, boxSizing: 'border-box'}}
                />

                {/*==DESCRIPCION==*/}
                <label style={{display:'block', fontSize: '12px', color: '#6b7280', marginBottom: '4px'}}>Descripción</label>
                <textarea
                value={description} 
                onChange={(e) => setDescription(e.target.value)}
                disabled={!isOwner}
                rows={3}
                style={{width: '100%', padding: '8px', marginBottom: '12px', borderRadius: '6px', border: '1px solid #d1d5db', fontSize: '13px', boxSizing: 'border-box', resize: 'vertical'}}
                />

                {/* FECHA LIMITE */}
                <div style={{display:'flex', gap: '10px', marginBottom: '12px'}}>
                    <div style={{ flex: 1}}>
                        <label style={{display: 'block', fontSize: '12px', color: '#6b7280', marginBottom: '4px'}}>Fecha límite</label>
                        <input
                        type="date"
                        value={dueDate}
                        onChange={(e) => setDueDate(e.target.value)}
                        disabled={!isOwner}
                        style={{width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #d1d5db', fontSize: '13px', boxSizing: 'border-box'}}
                        />
                    </div>

                    {/* RESPONSABLE */}
                    <div style={{ flex: 1}}>
                        <label style={{display:'block', fontSize: '12px', color: '#6b7280', marginBottom: '4px'}}>Responsable</label>
                        <select
                        value={assigneeId}
                        onChange={(e) => setAssigneeId(e.target.value)}
                        disabled={!isOwner}
                        style={{width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #d1d5db', fontSize: '13px', boxSizing: 'border-box'}}
                        >
                            <option value="">Sin asignar</option>
                            {users.map((u) => (
                                <option key={u.id} value={u.id}>{u.email}</option>
                            ))}
                        </select>
                    </div>
                </div>

                {/* Datos SOLO lectura, no pueden editarse */}
                <div style={{fontSize: '12px', color: '#6b7280', background: '#f9fafb', borderRadius: '6px', padding: '10px', marginBottom: '12px'}}>
                    <p style={{margin: '0 0 4px 0'}}>Creado por: {findUserEmail(card.creator_id) ?? '-'}</p>
                    <p style={{margin: '0 0 4px 0'}}>Creado: {new Date(card.created_at).toLocaleString()}</p>
                    {card.updated_at && <p style={{ margin: 0}}>Última actualización: {new Date(card.updated_at).toLocaleString()}</p>}
                </div>

                {!isOwner && (
                    <p style={{fontSize: '12px', color: '#d97706', marginBottom: '12px'}}>
                        Solo quien creó esta tarjeta puede editarla o eliminarla.
                    </p>
                )}

                {error && <p style={{fontSize: '12px', color: '#dc2626', marginBottom: '12px'}}>{error}</p>}

                <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                    {isOwner ? (
                        <button
                        onClick={handleDelete}
                        disabled={deleting || saving}
                        style={{padding: '8px 12px', background: 'transparent', border: '1px solid #fecaca', color: '#dc2626', borderRadius: '6px', fontSize: '12px', cursor: 'pointer'}}
                        >
                        {deleting ? 'Eliminando...' : 'Eliminar tarjeta'}
                        </button>
                    ) : <span />}

                    <div style={{ display: 'flex', gap: '8px'}}>
                        <button
                        onClick={onClose}
                        style={{ padding:'8px 14px', background: 'transparent', border: 'none', color:'#6b7280', fontSize:'13px', cursor: 'pointer'}}
                        >
                            Cerrar
                        </button>
                        {isOwner && (
                            <button
                            onClick={handleSave}
                            disabled={saving || deleting}
                            style={{padding: '8px 14px', background: '#2563eb', color: 'white', border: 'none', borderRadius: '6px', fontSize:'13px', cursor: 'pointer'}}
                            >
                                {saving ? 'Guardando...' : 'Guardar cambios'}
                            </button>
                        )}

                    {/* ELIMINAR TARJETA (SOLO CREADOR) */}
                    {isOwner ? (
                        <button onClick={handleDelete}>
                            Eliminar tarjeta
                        </button>
                    ) : <span />}
                    </div>
                </div>
            </div>
    </div>
    )
}