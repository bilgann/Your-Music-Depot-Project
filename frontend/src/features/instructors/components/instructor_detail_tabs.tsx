import Sections from "@/components/ui/sections";
import type { Credential, InstructorCompatibility } from "@/features/instructors/api/instructor_detail";
import type { Student } from "@/features/students/api/student";
import type { BlockedTime, Lesson } from "@/types/index";
import InstructorBlockedTimesTab from "@/features/instructors/components/instructor_blocked_times_tab";
import InstructorCompatibilityTab from "@/features/instructors/components/instructor_compatibility_tab";
import InstructorCredentialsTab from "@/features/instructors/components/instructor_credentials_tab";
import InstructorScheduleTab from "@/features/instructors/components/instructor_schedule_tab";
import InstructorStudentsTab from "@/features/instructors/components/instructor_students_tab";

interface Props {
    active: string;
    onChange: (key: string) => void;
    credentials: Credential[];
    schedule: Lesson[];
    students: Student[];
    compatibility: InstructorCompatibility[];
    blockedTimes: BlockedTime[];
    onAddCredential: () => void;
    onDeleteCredential: (credentialId: string) => void;
    onAddBlockedTime: () => void;
    onDeleteBlockedTime: (index: number) => void;
}

export default function InstructorDetailTabs({
    active,
    onChange,
    credentials,
    schedule,
    students,
    compatibility,
    blockedTimes,
    onAddCredential,
    onDeleteCredential,
    onAddBlockedTime,
    onDeleteBlockedTime,
}: Props) {
    return (
        <Sections
            active={active}
            onChange={onChange}
            sections={[
                {
                    key: "credentials",
                    label: "Credentials",
                    content: <InstructorCredentialsTab credentials={credentials} onAdd={onAddCredential} onDelete={onDeleteCredential} />,
                },
                {
                    key: "schedule",
                    label: "Schedule",
                    content: <InstructorScheduleTab lessons={schedule} />,
                },
                {
                    key: "students",
                    label: "Students",
                    content: <InstructorStudentsTab students={students} />,
                },
                {
                    key: "compatibility",
                    label: "Compatibility",
                    content: <InstructorCompatibilityTab items={compatibility} />,
                },
                {
                    key: "blocked-times",
                    label: "Blocked Times",
                    content: <InstructorBlockedTimesTab blockedTimes={blockedTimes} onAdd={onAddBlockedTime} onDelete={onDeleteBlockedTime} />,
                },
            ]}
        />
    );
}