/*

This on is better as we can pass it easily like so and reuse completely

<DynamicDropdown
  fetchUrl="http://localhost:8000/instructors"
  labelKey="name"
  valueKey="instructor_id"
  placeholder="Select instructor"
/>

*/


import { useState, useEffect } from "react";
import Select from "react-select";

type DropdownProps<T> = {
  fetchUrl: string;
  labelKey: keyof T;
  valueKey: keyof T;
  placeholder?: string;
};

export default function DynamicDropdown<T>({
  fetchUrl,
  labelKey,
  valueKey,
  placeholder = "Select an option"
}: DropdownProps<T>) {
  const [options, setOptions] = useState<T[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadOptions() {
      try {
        const res = await fetch(fetchUrl);
        const data = await res.json();
        setOptions(data);
      } finally {
        setLoading(false);
      }
    }

    loadOptions();
  }, [fetchUrl]);

  if (loading) return <p>Loading...</p>;

  return (
    <Select
      options={options.map((item) => ({
        value: item[valueKey],
        label: item[labelKey]
      }))}
      placeholder={placeholder}
    />
  );
}