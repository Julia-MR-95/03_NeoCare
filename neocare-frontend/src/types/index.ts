export interface User {
  id: number
  email: string
  full_name: string
  is_active: boolean
  created_at: string
}

//muestra horas wl por usuario en las tarjetas
export interface HoursPerUser {
  user_id: number
  user_email: string
  total_hours: number
}

export interface Card {
  id: number
  title: string
  description?: string
  list_id: number

  creator_id: number //para mostrar creador obligatorio

  assignee_id?: number | null //para mostrar responsable
  assignee?: User| null //mostrar nombre responsable

  //owner_id?: number
  due_date: string
  order: number
  created_at: string
  updated_at: string
  completed_at?: string
  
  total_hours?: number //hs totales EN cada tarjeta
  //labels?: Label[]
  hours_per_user?: HoursPerUser[] //wl trabajadas por usuario
}

export interface BoardList {
  id: number
  title: string   // "Pendiente" | "En Progreso" | "Revisión" | "Listo"
  board_id: number
  order: number
  cards: Card[]
}

export interface Board {
  id: number
  title: string
  owner_id: number
  created_at: string
}

export interface WorkLog {
  id: number
  card_id: number  
  user_id: number
  hours: number
  date: string
  note?: string
  is_automatic?: boolean
}

export interface HoursByCard {
  card_id: number
  card_title: string
  total_hours: number
}

export interface HoursByUser {
  user_id: number
  user_email: string
  total_hours: number
}

export interface Label {
  id: number
  title: string
  color: string
}