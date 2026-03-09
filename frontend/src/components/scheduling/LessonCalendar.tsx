/*
Scheduling Logic

The system needs to enforce these constraints:
A lesson is valid only if:

Instructor
    teaches the instrument
    student's skill ≥ instructor's minimum level
Room
    room supports the instrument
    capacity fits lesson type (private/group)
Time
    instructor not already teaching
    room not already booked
    student not already booked
*/