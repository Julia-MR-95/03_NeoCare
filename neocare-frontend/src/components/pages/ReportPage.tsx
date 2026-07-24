import { useEffect, useState } from 'react'
import apiClient from '../../api/clients'
import type { Board, HoursByCard, HoursByUser } from '../../types'

function toCSV(rows: Record<string, string | number>[]): string {
    if (rows.length === 0) return ''
    const headers = Object.keys(rows[0])
    const lines = [headers.join(',')]
    for (const row of rows) {
        lines.push(headers.map((h) => JSON.stringify(row[h] ?? '')).join(','))
    }
    return lines.join('\n')
}

function downloadCSV(filename: string, csv: string) {
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.click()
    URL.revokeObjectURL(url)
}

export default function ReportPage() {
    const [byCard, setByCard] = useState<HoursByCard[]>([])
    const [byUser, setByUser] = useState<HoursByUser[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        apiClient.get<Board[]>('/boards/').then(async (res) => {
            const board = res.data[0]
            if (!board) { setLoading(false); return }
            const [cardsRes, usersRes] = await Promise.all([
                apiClient.get<HoursByCard[]>(`/reports/board/${board.id}/hours-by-card`),
                apiClient.get<HoursByUser[]>(`/reports/board/${board.id}/hours-by-user`),
            ])
            setByCard(cardsRes.data)
            setByUser(usersRes.data)
            setLoading(false)
        })
    }, [])

    if (loading) return <div style={{ padding: '2rem'}}>Cargando informe...</div>

    return (
        <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto'}}>
            <h2 style={{ fontSize:'18px', marginBottom: '1rem'}}>Informe de horas</h2>

            <div style={{ display:'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1.5rem'}}>
                <h3 style={{ fontSize: '14px'}}>Horas por tarjeta</h3>
                <button onClick={() => downloadCSV('horas-por-tarjeta.csv', toCSV(byCard as any))}>Exportar CSV horas-tarjeta</button>
            </div>

            <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '8px' }}>
                <tbody>
                    {byCard.length === 0
                    ? <tr> <td style={{color:'#9ca3af', padding: '8px 0'}}>Sin datos todavía</td> </tr>
                    : byCard.map((r) => (
                        <tr key={r.card_id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                            <td style={{padding: '6px 0'}}>{r.card_title}</td>
                            <td style={{ textAlign: 'right'}}>{r.total_hours.toFixed(2)}</td>
                        </tr>
                    ))}
                </tbody>
            </table>

            <div style={{display:'flex', justifyContent:'space-between', alignItems: 'center', marginTop: '2rem'}}>
                <h3 style={{ fontSize: '14px' }}>Horas por usuario</h3>
                <button onClick={() => downloadCSV('horas-por-usuario.csv', toCSV(byUser as any))}>Exportar CSV horas-usuario</button>
            </div>
            <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '8px'}}>
                <tbody>
                    {byUser.length === 0
                    ? <tr><td style={{color: '#9ca3af', padding: '8px 0' }}>Sin datos todavía</td></tr>
                    : byUser.map((r) => (
                        <tr key={r.user_id} style={{borderBottom: '1px solid #f3f4f6'}}>
                            <td style={{ padding: '6px 0'}}>{r.user_email}</td>
                            <td style={{ textAlign: 'right'}}>{r.total_hours.toFixed(2)}h</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}