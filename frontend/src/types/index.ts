/* 

Setting tpyes for the dropdown's + form field's
- Julien
*/

export interface FormField {
    name: string;
    type: 'text' | 'number' | 'dropdown';
    label: string;
    placeholder?: string;
    fetchUrl?: string;
    labelKey?: string;
    valueKey?: string;
}

export interface FormConfig {
    title: string;
    fields: FormField[];
    endpoint: string;
}

export interface FormData {
    [key: string]: string | number | undefined;
}

export interface DropdownOption {
    [key: string]: string | number;
}

export type Lesson = {
  lesson_id: string
  course_id?: string | null
  instructor_id: string
  student_id?: string | null
  student_ids?: string[]
  room_id: string
  start_time: string
  end_time: string
  rate?: number | null
  status?: string | null
  recurrence?: string | null
  capacity?: number | null
  instrument?: { name: string; family: string } | null
}

export type Instructor = {
    instructor_id: string
    name: string
    email: string | null
    phone: string | null
}

export type Student = {
    student_id: string
    person_id: string
    client_id: string | null
    person: {
        person_id: string
        name: string
        email: string | null
        phone: string | null
    }
}

export type Room = {
    room_id: string
    name: string
    capacity: number | null
}

export type BlockedTime = {
    label: string;
    block_type: string;
    date?: string | null;
    date_range?: { period_start: string; period_end: string } | null;
    recurrence?: { rule_type: string; value: string } | null;
};