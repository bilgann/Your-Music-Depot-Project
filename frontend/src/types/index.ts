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
  lessonID: number
  instructorID: number
  studentID: number  
  roomID: number
  instrument: string
  lesson_type: string
  start_time: string
  end_time: string
  status: string
  date: string
  // Optional fields from joins
  instructorName?: string
  studentName?: string
  roomName?: string
}

export type Instructor = {
    instructorID: number
    name: string
    email: string
}

export type Student = {
    studentID: number
    name: string
    email: string
}

export type Room = {
    roomID: number
    room_name: string
    capacity: number
}