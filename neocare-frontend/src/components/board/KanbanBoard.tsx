import { useState } from 'react'
import { 
    DndContext, DragOverlay, PointerSensor, useSensor, 
    useSensors, closestCorners, type DragEndEvent 
} from '@dnd-kit/core'
import apiClient from '../../api/clients'
import KanbanColumn from './KanbanColumn'
import CardItem from './CardItem'
import { useAuth } from '../../context/AuthContext'
import type { BoardList, Card } from '../../types'
import { useNavigate } from 'react-router-dom'

interface Props {
    lists: BoardList[]
    setLists: React.Dispatch<React.SetStateAction<BoardList[]>>
}

export default function KanbanBoard({ lists, setLists}: Props) {
    const [activeCard, setActiveCard] = useState<Card | null>(null)
    const sensors= useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 5 }}))
    const { logout } = useAuth()
    const navigate = useNavigate()

    const findListByCardId = (cardId: number) => lists.find((l) => l.cards.some((c) => c.id === cardId))

    const parseListId = (droppableId: string | number): number | null => {
        const s = String(droppableId)
        if (s.startsWith('list-'))
            return Number(s.replace('list-', ''))
        const list = findListByCardId(Number(s))
        return list ? list.id : null
    }

    const handleDragStart = (event: { active: { id: string | number } }) => {
        const cardId = Number(event.active.id)
        const source = findListByCardId(cardId)
        setActiveCard(source?.cards.find((c) => c.id === cardId) ?? null)
    }

    const handleDragEnd = async (event: DragEndEvent) => {
        setActiveCard(null)
        const {active, over } = event
        if (!over) return

        const cardId = Number(active.id)
        const sourceList = findListByCardId(cardId)
        const targetListId = parseListId(over.id)
        if (!sourceList || targetListId === null) return

        const targetList = lists.find((l) => l.id === targetListId)
        if (!targetList) return

        const overCardIndex = targetList.cards.findIndex((c) => c.id === Number(over.id))
        const newOrder = overCardIndex >= 0 ? overCardIndex : targetList.cards.length

        const previousLists = lists //snapshot para revertir si falla

        //actualización tablero
        setLists((prev) => {
            const updated= prev.map((l) => ({...l, cards: [...l.cards]}))
            const src=updated.find((l) => l.id === sourceList.id)!
            const tgt = updated.find((l) => l.id === targetList.id)!
            const cardIndex = src.cards.findIndex((c) => c.id === cardId)
            const [card] = src.cards.splice(cardIndex, 1)
            tgt.cards.splice(newOrder, 0, { ...card, list_id: targetList.id})
            return updated
        })

        try {
            await apiClient.patch(`/cards/${cardId}/move`, {
                list_id: targetList.id,
                order: newOrder,
            })
        } catch (err:any) {
            setLists(previousLists) //revierte si el backend rechaza elmovimiento
            if (err?.response?.status === 403) {
                alert('Sólo quien creó esta tarjeta puede moverla.')
            }
        }
    }

    const handleCardCreated = (listId: number, card: Card) => {
        setLists((prev) => (
        prev.map((l) => (l.id === listId ? { ...l, cards: [...l.cards, card]} : l))
        )
    )
    }
    
    // Actualiza la tarjeta en estado local tras editarla en el modal de detalles 
    const handleCardUpdated = (updated: Card) => {
        setLists((prev) => 
            prev.map((l) => ({
            ...l,
            cards: l.cards.map((c) => c.id === updated.id ? { ...c, ...updated} : c),
            }))
        );
    };


    // quita la tarjeta del estado local tras borrarla 
    const handleCardDeleted = (cardId :number) => {
        setLists((prev) => 
            prev.map((l) => ({ 
                ...l, 
                cards: l.cards.filter((c) => c.id !== cardId),
            }))
        );
    };


    return (
        <div>   {/* Botón CERRAR SESION */}                                                                      
            <div style={{ display: 'flex', justifyContent: 'flex-end', padding: '1rem 1.5rem 0' }}>  
                <button
                    onClick={logout}
                    style={{ padding: '6px 12px', background: 'transparent', border: '1px solid #d1d5db', borderRadius: '6px', fontSize: '13px', color: '#6b7280', cursor: 'pointer' }}
                >
                    Cerrar sesión
                </button>
            </div>
            <div 
                style={{display: 'flex',justifyContent: 'flex-end',gap: '1rem',marginBottom: '1rem',}}
            > {/* ACCESO /HOURS Y /REPORTS */}
                <button onClick={() => navigate('/hours')}>
                    Mis horas
                </button>

                <button onClick={() => navigate('/reports')}>
                    Informes
                </button>
            </div>   
        <DndContext
            sensors={sensors}
            collisionDetection={closestCorners}
            onDragStart={handleDragStart}
            onDragEnd={handleDragEnd}
        >
            <div style={{ display: 'flex', gap:'1rem', padding: '1.5rem', overflowX: 'auto'}}>
                {lists.map((list) => (
                    <KanbanColumn 
                    key={list.id} 
                    list={list} 
                    onCardCreated={handleCardCreated}
                    onCardUpdated={handleCardUpdated}
                    onCardDeleted={handleCardDeleted}
                     />
                ))}
            </div>
            <DragOverlay>
                {activeCard && (
                    <CardItem 
                    card={activeCard}
                    listTitle=""
                    onCardUpdated={() => {}}
                    onCardDeleted={() => {}}
                    />
                )}
                </DragOverlay>
            </DndContext>
        </div>
    )
}