"use client";

import { useRouter } from "next/navigation";
import type { Student } from "@/features/students/api/student";

interface Props {
    students: Student[];
}

export default function InstructorStudentsTab({ students }: Props) {
    const router = useRouter();

    if (students.length === 0) {
        return <p className="table-empty">No active students found for this instructor.</p>;
    }

    return (
        <div className="data-table-wrapper">
            <table className="data-table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Phone</th>
                    </tr>
                </thead>
                <tbody>
                    {students.map((student) => (
                        <tr
                            key={student.student_id}
                            className="table-row-clickable"
                            onClick={() => router.push(`/students/${student.student_id}`)}
                        >
                            <td>{student.person.name}</td>
                            <td>{student.person.email || "--"}</td>
                            <td>{student.person.phone || "--"}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}