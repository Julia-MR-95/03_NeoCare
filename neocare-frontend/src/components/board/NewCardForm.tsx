import { useEffect, useState } from "react"
import apiClient from "../../api/clients"
import type { Card, User } from '../../types'

interface Props {
    listId: number
    onCardCreated: (card: Card) => void
    onCancel: () => void
}

export default function NewCardForm({
    listId,
    onCardCreated,
    onCancel,
}: Props) {
    const [users, setUsers] = useState<User[]>([])

    const [title, setTitle] = useState('')
    const [description, setDescription] = useState('')
    const [dueDate, setDueDate] = useState('')
    const [assigneeId, setAssigneeId] = useState('')

    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    useEffect (() =>{
        apiClient
        .get<User[]>('/users')
        .then((res) => setUsers(res.data))
        .catch(() => {})
    }, [])

    const handleSubmit = async() => {
        if (!title.trim()) {
            setError('El título es obligatorio.')
            return
        }

        setLoading(true)
        setError(null)

        try{
            const res = await apiClient.post<Card>('/cards/', {
                list_id:listId,
                title: title.trim(),
                description: description.trim() || null,
                due_date: dueDate
                    ? new Date(dueDate).toISOString()
                    : null,
                assignee_id: assigneeId
                    ? Number(assigneeId)
                    : null,
            })

            onCardCreated(res.data)

            setTitle('')
            setDescription('')
            setDueDate('')
            setAssigneeId('')

            onCancel()
        } catch {
            setError('No se pudo crear la tarjeta')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div style={{marginTop:'10px', padding:'12px', background: 'white', borderRadius: '8px', border: '1px solid #e5e7eb'
        }}
        >
            {/* TÍTULO */}
            <input 
            placeholder="Título"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            style={{width: '100%', padding: '8px', marginBottom: '1opx', borderRadius: '6px', border: '1px solid #d1d5db', boxSizing: 'border-box'
            }}
            />

            {/* DESCRIPCIÓN */}
            <textarea
            placeholder="Descripción"
            rows={3}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            style={{width: '100%',padding: '8px', marginBottom: '10px', borderRadius:'6px', border: '1px solid #d1d5db', resize: 'vertical', boxSizing: 'border-box', 
            }}
            />

            {/* FECHA LÍMITE */}
            <input
            type="date"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            style={{width:'100%', padding:'8px', marginBottom:'10px', borderRadius:'6px', border:'1px solid #d1d5db', boxSizing:'border-box',
            }}
            />

            {/* RESPONSABLE */}
            <select
            value={assigneeId}
            onChange={(e) => setAssigneeId(e.target.value)}
            style={{width:'100%', padding:'8px', marginBottom:'10px', borderRadius:'6px', border:'1px solid #d1d5db', boxSizing: 'border-box',
            }}
            >
                <option value="">Sin asignar.</option>
                {users.map((u) => (
                    <option key={u.id} value={u.id}>
                        {u.email}
                    </option>
                ))}
            </select>

            {error && (
                <p
                style={{color:'#dc2626', fontSize:'12px', marginBottom:'10px',
                }}
            >
                {error}
            </p>
            )}
            
            {/* BOTÓN AÑADIR */}
            <div
            style={{display:'flex', justifyContent:'space-between',
            }}
            >
            <button
            onClick={handleSubmit}
            disabled={loading}
            style={{padding:'8px 14px', background:'#2563eb', color:'white', border:'none', borderRadius:'6px', cursor:'pointer',
            }}
            >
            {loading? 'Creando...' : 'Añadir'}
            </button>

            {/* BOTÓN CANCELAR */}
            <button
            onClick={onCancel}
            style={{padding:'8px 14px', background:'transparent', border:'none', color:'#6b7280', cursor:'pointer',
            }}
            >
                Cancelar
            </button>
            </div>
        </div>
    )
}