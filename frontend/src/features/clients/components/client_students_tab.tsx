import type { ClientStudent } from "@/features/clients/api/client";

interface Props {
    students: ClientStudent[];
}

export default function ClientStudentsTab({ students }: Props) {
    if (students.length === 0) {
        return <p className="table-empty">No students linked to this client.</p>;
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
                    {students.map((stu) => (
                        <tr key={stu.student_id}>
                            <td>{stu.person.name}</td>
                            <td>{stu.person.email || "--"}</td>
                            <td>{stu.person.phone || "--"}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
