/*
Responsible for rendering one lesson block on the calendar
*/

interface Lesson {
    status?: string | null;
    start_time: string;
    end_time: string;
}

export default function LessonEvent({ lesson }: { lesson: Lesson }) {
    return (
        <div className="lesson-event">
            <b>{lesson.status ?? 'Lesson'}</b>
            <div>{lesson.start_time} - {lesson.end_time}</div>
        </div>
    )
}
