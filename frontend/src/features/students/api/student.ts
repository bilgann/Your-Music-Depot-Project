import { apiFetch, apiJsonPaged } from "@/lib/api";

export type TeachingRequirement = {
    requirement_type: "credential" | "min_student_age" | "max_student_age";
    value: string;
};

export type Student = {
    student_id: string;
    person_id: string;
    client_id: string | null;
    age?: number | null;
    requirements?: TeachingRequirement[];
    person: {
        person_id: string;
        name: string;
        email: string | null;
        phone: string | null;
    };
    client?: {
        client_id: string;
        person: { name: string };
    } | null;
};

export async function getStudents(): Promise<Student[]> {
    const res = await apiFetch("/api/students");
    if (!res.ok) throw new Error(`Failed to fetch students: ${res.statusText}`);
    const body = await res.json();
    return body.data ?? [];
}

export async function listStudents(
    page = 1,
    pageSize = 20,
    search?: string
): Promise<{ data: Student[]; total: number }> {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
    if (search) params.set("search", search);
    return apiJsonPaged<Student>(`/api/students?${params}`);
}

export async function createStudent(data: {
    name: string;
    email?: string;
    phone?: string;
    client_id?: string;
    age?: number;
    requirements?: TeachingRequirement[];
}): Promise<Student> {
    const res = await apiFetch("/api/students", {
        method: "POST",
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(`Failed to create student: ${res.statusText}`);
    const body = await res.json();
    return body.data;
}

export async function updateStudent(studentId: string, data: {
    name?: string;
    email?: string;
    phone?: string;
    client_id?: string;
    age?: number;
    requirements?: TeachingRequirement[];
}): Promise<Student> {
    const res = await apiFetch(`/api/students/${studentId}`, {
        method: "PUT",
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(`Failed to update student: ${res.statusText}`);
    const body = await res.json();
    return body.data;
}

export async function deleteStudent(studentId: string): Promise<void> {
    const res = await apiFetch(`/api/students/${studentId}`, { method: "DELETE" });
    if (!res.ok) throw new Error(`Failed to delete student: ${res.statusText}`);
}

export type StudentEnrollment = {
    enrollment_id: string;
    attendance_status: string | null;
    enrolled_at: string;
    lesson: {
        lesson_id: string;
        start_time: string;
        end_time: string;
        status: string | null;
        rate: number | null;
        instructor: { name: string } | null;
        room: { name: string } | null;
    };
};

export type StudentInvoice = {
    invoice_id: string;
    period_start: string;
    period_end: string;
    total_amount: number;
    amount_paid: number;
    status: string;
};

export async function getStudentById(studentId: string): Promise<Student> {
    const res = await apiFetch(`/api/students/${studentId}`);
    if (!res.ok) throw new Error(`Failed to fetch student: ${res.statusText}`);
    const body = await res.json();
    return body.data;
}

export async function getStudentLessons(studentId: string): Promise<StudentEnrollment[]> {
    const res = await apiFetch(`/api/students/${studentId}/lessons`);
    if (!res.ok) throw new Error(`Failed to fetch student lessons: ${res.statusText}`);
    const body = await res.json();
    return body.data ?? [];
}

export async function getStudentInvoices(studentId: string): Promise<StudentInvoice[]> {
    const res = await apiFetch(`/api/students/${studentId}/invoices`);
    if (!res.ok) throw new Error(`Failed to fetch student invoices: ${res.statusText}`);
    const body = await res.json();
    return body.data ?? [];
}
