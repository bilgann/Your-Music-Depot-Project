import { useCallback, useEffect, useMemo, useState } from "react";
import { listCourses } from "@/features/courses/api/course";
import { getInstructors } from "@/features/instructors/api/instructor";
import type { Course } from "@/features/courses/api/course";
import type { Instructor } from "@/features/instructors/api/instructor";

const PAGE_SIZE = 20;

export function useCourses() {
    const [allCourses, setAllCourses] = useState<Course[]>([]);
    const [instructors, setInstructors] = useState<Instructor[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [page, setPage] = useState(1);
    const [search, setSearchRaw] = useState("");

    const instructorNames = useMemo(
        () => Object.fromEntries(instructors.map((instructor) => [instructor.instructor_id, instructor.name])),
        [instructors]
    );

    const filteredCourses = useMemo(() => {
        const query = search.trim().toLowerCase();
        if (!query) return allCourses;

        return allCourses.filter((course) => {
            const leadInstructorNames = course.instructor_ids.map((id) => instructorNames[id] ?? id).join(" ");
            const haystack = [
                course.name,
                course.description ?? "",
                course.status,
                course.period_start,
                course.period_end,
                leadInstructorNames,
            ].join(" ").toLowerCase();

            return haystack.includes(query);
        });
    }, [allCourses, instructorNames, search]);

    const total = filteredCourses.length;
    const pageCount = Math.max(1, Math.ceil(total / PAGE_SIZE));

    const courses = useMemo(() => {
        const startIndex = (page - 1) * PAGE_SIZE;
        return filteredCourses.slice(startIndex, startIndex + PAGE_SIZE);
    }, [filteredCourses, page]);

    const refresh = useCallback(async () => {
        try {
            setLoading(true);
            const [courseData, instructorData] = await Promise.all([
                listCourses(),
                getInstructors(),
            ]);
            setAllCourses(courseData);
            setInstructors(instructorData);
            setError(null);
        } catch {
            setError("Could not load courses.");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => { void refresh(); }, [refresh]);

    useEffect(() => {
        if (page > pageCount) {
            setPage(pageCount);
        }
    }, [page, pageCount]);

    function setSearch(searchValue: string) {
        setSearchRaw(searchValue);
        setPage(1);
    }

    return { courses, instructors, loading, error, refresh, page, setPage, search, setSearch, total, pageCount };
}