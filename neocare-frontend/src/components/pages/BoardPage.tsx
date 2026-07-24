import { useEffect, useState } from "react"
import apiClient from '../../api/clients'
import type { BoardList, Board } from "../../types" 
import KanbanBoard from "../board/KanbanBoard"

const DEFAULT_COLUMNS=['Pendiente', 'En progreso', 'Revisión', 'Completado']

export default function BoardPage() {
    const [lists, setLists] = useState<BoardList[]>([])
    const [loading, setLoading] = useState(true)
    const[error, setError] = useState<string | null>(null)
    
    useEffect(() => {
        loadBoard()
    }, [])

    const loadBoard = async () => {
        setLoading(true)
        setError(null)
        try{
            //crear/obtener tablero del usuario
            const boardsRes = await apiClient.get<Board[]>('/boards/')
            let board = boardsRes.data[0]
            if (!board) {
                const created = await apiClient.post<Board>('/boards/', { title: 'Mi tablero'})
                board = created.data
            }

            //obtener/crear las listas del tablero por defecto
            const listsRes = await apiClient.get<BoardList[]>(`/lists/board/${board.id}`)
            let boardLists  = listsRes.data

            if (boardLists.length === 0) {
                const createdLists = await Promise.all(
                    DEFAULT_COLUMNS.map((title, order) =>
                    apiClient.post<BoardList>('/lists/', { title, board_id: board.id, order })
                    )
                )
                boardLists = createdLists.map((r) => r.data)
            }

            //obtener las tarjetas de cada lista
            const listsWithCards = await Promise.all(
                boardLists
                .sort((a,b) => a.order - b.order)
                .map(async (list) => {
                    const cardsRes = await apiClient.get(`/cards/list/${list.id}`)
                    return { ...list, cards: cardsRes.data.sort((a: any, b:any) => a.order - b.order) }
                })
            )

            setLists(listsWithCards)
        } catch {
            setError('No se pudo cargar el tableto. Inténtelo de nuevo.')
        } finally {
            setLoading(false)
        }
    }

    if (loading) return <div style={{ padding: '2rem'}}>Cargando tablero...</div>
    if (error) return <div style={{ padding: '2rem', color: '#dc2626' }}>{error}</div>

    return <KanbanBoard lists={lists} setLists={setLists} />
}