import Sections from "@/components/ui/sections";
import CourseInstructorsTab from "@/features/courses/components/course_instructors_tab";
import CourseRateTab from "@/features/courses/components/course_rate_tab";
import CourseRosterTab from "@/features/courses/components/course_roster_tab";
import CourseScheduleTab from "@/features/courses/components/course_schedule_tab";
import type { Course, CourseOccurrence } from "@/features/courses/api/course";
import type { Instructor } from "@/features/instructors/api/instructor";
import type { Student } from "@/features/students/api/student";

type Option = { value: string; label: string };

interface Props {
    active: string;
    onChange: (key: string) => void;
    course: Course;
    roster: Student[];
    assignedInstructors: Instructor[];
    availableInstructorOptions: Option[];
    occurrences: CourseOccurrence[];
    saving: boolean;
    projecting: boolean;
    onOpenEnrollModal: () => void;
    onUnenrollStudent: (studentId: string) => void;
    onProjectSchedule: () => void;
    onAddInstructor: (instructorId: string) => void;
    onRemoveInstructor: (instructorId: string) => void;
}

export default function CourseDetailTabs({
    active,
    onChange,
    course,
    roster,
    assignedInstructors,
    availableInstructorOptions,
    occurrences,
    saving,
    projecting,
    onOpenEnrollModal,
    onUnenrollStudent,
    onProjectSchedule,
    onAddInstructor,
    onRemoveInstructor,
}: Props) {
    return (
        <Sections
            active={active}
            onChange={onChange}
            sections={[
                {
                    key: "roster",
                    label: "Roster",
                    content: (
                        <CourseRosterTab
                            students={roster}
                            saving={saving}
                            onOpenEnrollModal={onOpenEnrollModal}
                            onUnenroll={onUnenrollStudent}
                        />
                    ),
                },
                {
                    key: "schedule",
                    label: "Schedule",
                    content: (
                        <CourseScheduleTab
                            occurrences={occurrences}
                            projecting={projecting}
                            onProject={onProjectSchedule}
                        />
                    ),
                },
                {
                    key: "instructors",
                    label: "Instructors",
                    content: (
                        <CourseInstructorsTab
                            instructors={assignedInstructors}
                            availableOptions={availableInstructorOptions}
                            saving={saving}
                            onAdd={onAddInstructor}
                            onRemove={onRemoveInstructor}
                        />
                    ),
                },
                {
                    key: "rate",
                    label: "Rate",
                    content: <CourseRateTab course={course} />,
                },
            ]}
        />
    );
}