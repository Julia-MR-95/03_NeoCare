import { useState } from 'react'
import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import apiClient from '../../api/clients'
import CardDetailModal from './CardDetailModal' //detalles de tarjetas
import type { Card } from '../../types'

//fecha de hoy en formato YYYY-MM-DD
const today = () => new Date().toISOString().slice(0,10)

//detalles tarjetas
interface Props {
    card: Card
    listTitle: string
    onCardUpdated: (card: Card) => void
    onCardDeleted: (cardId: number) => void
}

export default function CardItem({ card , listTitle, onCardUpdated, onCardDeleted }: Props) {
    const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: card.id })

    const style= {
        transform: CSS.Transform.toString(transform),
        transition,
        opacity: isDragging ? 0.4 : 1,
        touchAction: 'none' as const, //para evitar que seleccione texto por el retardo de 5ms
    }

    const isOverdue = card.due_date && new Date(card.due_date) < new Date()

    // estado del formulario manual para registrar horas
    const [logging, setLogging] = useState(false)
    const [hours, setHours] = useState('')
    const [date, setDate] = useState(today())
    const [note, setNote] = useState('')
    const [submitting, setSubmitting] = useState(false)
    const [justLogged, setJustLogged] = useState(false)
    //total de hs mostradas EN la tarjeta
    //inicia con lo q viene del backend
    //(card.total_hours),
    //incrementa tras guardar manual sin recarga del tablero
    const [displayedTotal, setDisplayedTotal] = useState(card.total_hours ?? 0) 
    //para mostrar datos tarjetas
    const [showDetail, setShowDetail] = useState(false)

    //evitamos que el click intente iniciar un arrastre de la tarjeta
    const stopDrag = (e: React.SyntheticEvent) => e.stopPropagation()

    const handleLogHours = async () => {
        const hoursNum = parseFloat(hours)
        if (!hoursNum || hoursNum < 0.25) {
            alert('Introduce al menos 15 minutos (0.25 horas)')
            return
        }
        setSubmitting(true)
        try {
            await apiClient.post('/worklogs/', {
                card_id: card.id,
                hours: hoursNum,
                date: new Date(date).toISOString(),
                note: note.trim() || undefined,
            })
            setHours('')
            setNote('')
            setLogging(false) 
            setJustLogged(true) //justLogged para mostrar q se registran las horas correctamente plq tiene que ser TRUE
            setDisplayedTotal((t) => Math.round((t+hoursNum) *100) / 100)
            setTimeout(() => setJustLogged(false), 2000)
        } catch {
            alert('No se pudieron guardar las horas. Inténtalo de nuevo.')
        } finally {
            setSubmitting(false)
        }
    }

    return (
    <div
        ref={setNodeRef}
        style={style}
        {...attributes}
        {...listeners}
        className="kanban-card"
        >
            {/* TÍTULO */}
            <p
                onPointerDown={stopDrag}
                onClick={() => setShowDetail(true)}
                style={{fontSize:'13px', fontWeight: 500, marginBottom: '4px', cursor: 'pointer'}}
                >
                    {card.title}
                </p>
            {/* <p style={{ fontSize: '13px', fontWeight: 500, marginBottom: '4px'}} > {card.title} </p>*/}

            {/* RESPONSABLE */}
            {card.assignee && (
                <p
                style={{fontSize: '11px', color:'#6b7280', marginBottom:'6px'
                }}
                >
                   * {card.assignee.full_name}
                </p>
            )}

            {/* HORAS USUARIO */}
            {displayedTotal > 0 && (
                <div style={{ fontSize:'11px', color:'#4b5563', marginBottom:'4px'}}>
                    <p style={{margin: '0 0 2px 0' }}> Total: {displayedTotal.toFixed(2)}h</p>
                    {(card.hours_per_user ?? []).map((u) => (
                        <p key={u.user_id} style ={{margin: '0', paddingLeft: '12px', color: '#6b7280'}}>
                            {u.user_email.split('@')[0]}: {u.total_hours.toFixed(2)}h 
                        </p>
                    ))}
                    {/*Total: {displayedTotal.toFixed(2)}h*/}
                </div>
            )}

            {/* DESCRIPCIÓN */}
            {card.description && (
                <p style={{ fontSize: '12px', color: '#6b7280', marginBottom: '6px'}} >
                    {card.description.length > 80 ? card.description?.slice(0,80) + '...' : card.description}
                </p>
            )}

            {/* FECHA LÍMITE */}
            {card.due_date && (
                <span style={{ fontSize: '11px', color: isOverdue ? '#dc2626' : '#9ca3af', marginBottom: '6px' }}>
                    {isOverdue ? 'Atención' : ''}
                    Fecha límite: {new Date(card.due_date).toLocaleDateString()} 
                </span>
            )}
            {/* FECHA COMPLETADO */}
            {card.completed_at && (
                <p style={{ fontSize: '11px', color: '#16a34a', marginTop: '4px'}}>
                    {(
                        (new Date(card.completed_at).getTime() - new Date(card.created_at).getTime()) / 3600000
                    ).toFixed(2)} horas automáticas (desde creación hasta completado)
                </p>
            )}

            {justLogged && (
                <p style={{ fontSize: '11px', color: '#16a34a', marginTop: '6px'}}>Horas registradas correctamente</p>
            )}

            {logging ? (
                <div 
                onPointerDown={stopDrag}
                style={{ marginTop: '8px', paddingTop: '8px', borderTop: '1px solid #e5e7eb'}}>
                    <div style={{flexDirection:'column', gap:'6px', marginBottom:'6px'}}>
                        <input
                        type="number"
                        step="0.25"
                        min="0.25"
                        placeholder="Horas"
                        value={hours}
                        onChange={(e) => setHours(e.target.value)}
                        style={{ width:'70px', padding:'6px', fontSize: '12px', borderRadius: '6px', border: '1px solid #d1d5db' }}/>
                        <input 
                        type="date"
                        value={date}
                        onChange={(e) => setDate(e.target.value)}
                        style={{ flex: 1, padding: '6px', fontSize: '12px', borderRadius: '6px', border: '1px solid #d1d5db'}}/>
                    </div>
                    <input 
                    type="text"
                    placeholder='Nota (opcional)'
                    value={note}
                    onChange={(e) => setNote(e.target.value)}
                    maxLength={200}
                    style={{ width: '100%', padding: '6px', fontSize: '12px', borderRadius: '6px', border: '1px solid #d1d5db', boxSizing: 'border-box', marginBottom: '6px'}} />
                    <div style={{flexDirection:'column', gap: '6px'}}>
                        <button
                        onClick={handleLogHours}
                        disabled={submitting}
                        style={{padding:'5px 10px', background: '#2563eb', color: 'white', border: 'none', borderRadius: '6px', fontSize:'12px', cursor: 'pointer'}}>
                            {submitting ? 'Guardando...' : 'Guardar'}
                        </button>
                        <button
                        onClick={() => setLogging(false)}
                        style={{padding: '5px 10px', background: 'transparent', border: 'none', color: '#6b7280', fontSize: '12px', cursor: 'pointer' }}>
                            Cancelar
                        </button>
                    </div>
                </div>    
            ) : (
                <button
                onPointerDown={stopDrag}
                onClick={() => setLogging(true)}
                style={{marginTop: 'auto', display: 'block', width:'100%', textAlign:'center', padding: '4px 0', background:'transparent', border:'none', color:'#2563eb', fontSize:'11px', cursor: 'pointer' }}>
                    Registrar horas
                </button>
            )}
            {/*el modal de detalle se muestra solo cuando showDetail es true */}
            {showDetail && (
                <CardDetailModal
                card={card}
                listTitle={listTitle}
                onClose={() => setShowDetail(false)}
                onUpdated={onCardUpdated}
                onDeleted={onCardDeleted}
                />
            )}
    </div>
    )
}