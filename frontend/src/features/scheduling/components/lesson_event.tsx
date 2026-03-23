/*
Responsible for rendering one lesson block on the calendar
*/

interface Lesson {
    instrument: string;
    instructorName: string;
    start_time: string;
    end_time: string;
}

export default function LessonEvent({ lesson }: { lesson: Lesson }){
    return (
        <div className="lesson-event">
            <b>{lesson.instrument}</b>
            <div>{lesson.instructorName}</div>
            <div>{lesson.start_time} - {lesson.end_time}</div>
        </div>
    )
}