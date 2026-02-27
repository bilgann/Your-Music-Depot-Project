/* 

Inside of the central dashboard there will be a button
to add Lessons this will be called as a pop-up to add
a new lesson

Lessons Contains:

1. instructor
2. Student
3. room
4. instrument
5. start_time
6. end_time
7. Date

The user will half to enter all of this information

Idea:
DropDown w/ list of X and can search

*/

export default function AddLessons () {

    

    function submitButton() {
        //Validation
    };

    

    return (

        <div className="form-container">

            <input id='teacher-input' className='dropdown' placeholder='Enter Teacher Name'></input>
            <a>Add new Teacher</a>

            <button onClick={submitButton}>Submit Lesson</button>

        </div>

    );
}