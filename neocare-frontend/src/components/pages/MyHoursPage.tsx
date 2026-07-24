import { useEffect, useState } from 'react'
import apiClient from '../../api/clients'
import type { WorkLog } from '../../types'

const DAY_NAMES = [ 'Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab', 'Dom' ]

function startOfWeek(date: Date): Date {
    const d = new Date(date)
    const day = (d.getDate() + 6) % 7 //lunes = 0
    d.setDate(d.getDate() - day)
    d.setHours(0,0,0,0)
    return d
}

export default function MyHoursPage() {
    const [logs, setLogs] = useState<WorkLog[]>([])
    const [loading, setLoading] = useState(true)
    const [weekStart, setWeekStart] = useState (() => startOfWeek(new Date()))
    
    useEffect(() => {
        apiClient.get<WorkLog[]>('/worklogs/my-logs')
        .then((res) => setLogs(res.data))
        .finally(() => setLoading(false))
    }, [])

    const weekEnd = new Date(weekStart)
    weekEnd.setDate(weekEnd.getDate() + 6)

    const weekLogs = logs.filter((log) => {
        const d = new Date(log.date)
        return d >= weekStart && d <= weekEnd
    })

    const totalsByDay = Array.from({ length: 7 }, (_,i) => {
        const day = new Date(weekStart)
        day.setDate(day.getDate() + i)
        const dayLogs = weekLogs.filter((l) => new Date(l.date).toDateString() === day.toDateString())
        return { day, hours: dayLogs.reduce((sum, l) => sum + l.hours, 0), logs: dayLogs }
    })

    const weekTotal = weekLogs.reduce((sum, l) => sum + l.hours, 0)

    if (loading) return <div style={{ padding: '2rem' }}>Cargando...</div>

    return (
        <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem'}}>
                <button onClick={() => setWeekStart((w) => { const n = new Date (w); n.setDate(n.getDate() - 7); return n })}>
                    Semana anterior
                </button>
                <h2 style={{ fontSize: '16px'}}>
                {weekStart.toLocaleDateString()} - {weekEnd.toLocaleDateString()}
                </h2>
                <button onClick={() => setWeekStart((w) => {const n = new Date(w); n.setDate(n.getDate() + 7); return n})}>
                    Semana siguiente
                </button>
            </div>
            
            {weekTotal === 0 ? (
                <p style={{ color: '#9ca3af' }}>No hay horas registradas esta semana.</p>
            ) : (
                <table style={{width: '100%', borderCollapse: 'collapse' }} >
                    <thead>
                        <tr style={{ textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>
                            <th style={{ padding: '8px 0'}}>Día</th>
                            <th>Horas</th>
                            <th>Notas</th>
                        </tr>
                    </thead>
                    <tbody>
                        {totalsByDay.map(({ day, hours, logs: dayLogs }, i) => (
                            <tr key={i} style={{ borderBottom: '1px solid #f3f4f6' }} >
                                <td style={{ padding: '8px 0'}}>{DAY_NAMES[i]} {day.getDate()}/{day.getMonth() + 1 }</td>
                                <td>{hours > 0 ? hours.toFixed(2): '-'}</td>
                                <td style={{ fontSize: '12px', color: '#6b7280' }}>
                                    {dayLogs.map((l) => l.note).filter(Boolean).join(', ')}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                    <tfoot>
                        <tr>
                            <td style={{ padding: '8px 0', fontWeight: 600}}>Total semana</td>
                            <td style={{ fontWeight: 600}}>{weekTotal.toFixed(2)}</td>
                            <td />
                        </tr>
                    </tfoot>
                </table>
            )}
        </div>
    )
}