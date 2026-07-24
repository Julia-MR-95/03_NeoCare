import { useState } from 'react'
import { useDroppable } from "@dnd-kit/core"
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable'
//import apiClient from '../../api/clients'
import CardItem from './CardItem'
import NewCardForm from './NewCardForm'
import type { BoardList, Card } from "../../types"
 

/// === INTERFAZ ===

const COLUMN_COLORS: Record <string, string> = { //devuelve un string independientemente del objeto que se ponga
        'Pendiente': '#6b7280',
        'En progreso': '#2563eb',
        'Revisión': '#d97706',
        'Completado': '#16a34a'
    }

interface Props {
    list: BoardList
    onCardCreated: (listId: number, card: Card) => void //para crear una nueva tarjeta directamente desde el tablero
    onCardUpdated: (card: Card) => void
    onCardDeleted: (cardId: number) => void
}

export default function KanbanColumn({ list, onCardCreated, onCardUpdated, onCardDeleted }: Props) {
    const {setNodeRef} = useDroppable({ id: `list-${list.id}`})
    const cardIds = list.cards.map((c) => c.id)

    const [adding, setAdding] = useState(false)

    return (
    <div style={{ minWidth: '280px', background: '#f3f4f6', borderRadius: '10px', padding: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1rem'}}>
            <span style={{ 
                width: '8px', 
                height: '8px', 
                borderRadius: '50%', 
                background: COLUMN_COLORS[list.title] ?? '#6b7280',
            }} 
            />
            <h3 style= {{ fontSize: '14px', fontWeight: 600}} > {list.title}</h3>
            <span style={{ marginLeft: 'auto', fontSize: '12px', color: '#9ca3af'}} > {list.cards.length}</span>
        </div>

        <div ref={setNodeRef} style={{minHeight: '60px', display:'flex', flexDirection:'column', gap: '8px'}}>
            <SortableContext items={cardIds} strategy={verticalListSortingStrategy}>
                {list.cards.length === 0 && !adding ? ( //adding evita que el mensaje "sin tarjetas" tape el formulario mientras se escribe
                    <div style={{ textAlign: 'center', padding: '2rem 1rem', color: '#9ca3af', fontSize: '13px'}}>
                        Sin tarjetas todavía.
                    </div>
                ) : (
                   list.cards.map((card) => (
                    <CardItem
                    key={card.id}
                    card={card}
                    listTitle={list.title}
                    onCardUpdated={onCardUpdated}
                    onCardDeleted={onCardDeleted}
                    />
                   )) 
                )}
            </SortableContext>
        </div>

        {adding ? (
            <NewCardForm
            listId={list.id}
            onCardCreated={(card) => {
                onCardCreated(list.id, card)
                setAdding(false)
            }}
            onCancel={() => setAdding(false)}
            />
        ) : (
            <button
            onClick={() => setAdding(true)}
            style={{width:'100px', marginTop:'8px',background:'transparent',border:'none',color:'#6b7280',fontSize:'13px',textAlign:'left',cursor:'pointer'
            }}
        >
            == NUEVA TARJETA ==
        </button>
        )}
    </div>
    )
}
