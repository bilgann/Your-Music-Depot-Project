/*

I'm making this component as a tester to seeing if I can
create a reusable one so we can just paste the component
in the forms we need and than pass whatever we need to through it
I'm unsure if creating each drop down individually is good for
the end product, however it's a good starter to see how this
will work overall

Can DELETE!!! - Julien, I think my other version would be better

*/

import { useState, useEffect } from "react";
import Select from "react-select"; // or your UI library

type Instructor = {
  instructor_id: number;
  name: string;
};

export default function InstructorDropdown() {
  const [instructors, setInstructors] = useState<Instructor[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadInstructors() {
      try {
        const res = await fetch("http://localhost:8000/instructors");
        const data = await res.json();
        setInstructors(data);
      } finally {
        setLoading(false);
      }
    }

    loadInstructors();
  }, []); // runs once on mount

  if (loading) return <p>Loading...</p>;

  return (
    <Select
      options={instructors.map((i) => ({
        value: i.instructor_id,
        label: i.name,
      }))}
      placeholder="Select an instructor"
    />
  );
}