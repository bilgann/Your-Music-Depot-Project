/*

This on is better as we can pass it easily like so and reuse completely

<DynamicDropdown
  fetchUrl="http://localhost:8000/instructors"
  labelKey="name"
  valueKey="instructor_id"
  placeholder="Select instructor"
/>

*/


import React, { useState, useEffect } from "react";
import { DropdownOption } from "@/types";
/* import Select from "react-select"; */


interface DropdownProps {
  fetchUrl?: string;
  labelKey?: string;
  valueKey?: string;
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
}

const Dropdown: React.FC<DropdownProps> = ({
  fetchUrl,
  labelKey = 'name',
  valueKey = 'id',
  placeholder = ' Select...',
  value,
  onChange
}) => {

  const [options, setOptions] = useState<DropdownOption[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (fetchUrl) {
      const fetchOptions = async () => {
        try {
          setLoading(true);
          const response = await fetch(fetchUrl);
          const data = await response.json();
          setOptions(data);
        } catch (err) {
          setError(`Failed to Load: ${labelKey} options`)
          console.log(err)
        } finally {
          setLoading(false);
        }
      };

      fetchOptions();

    }

  }, [fetchUrl, labelKey]);

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedValue = e.target.value;
    onChange(selectedValue);
  };

  return (
    <select
      value={value || ''}
      onChange={handleChange}
      disabled={loading}
    >

      <option value="">{placeholder}</option>
      {loading ? (
        <option value="">Loading...</option>
      ) : error ? (
        <option value="">Error loading options</option>
      ) : (
        options.map((option) => (
          <option
            key={option[valueKey]}
            value={option[valueKey]}
          >
            {option[labelKey]}
          </option>
        ))
      )}
    </select>
  );
};

export default Dropdown;

/* DropdownProps<T> = {
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
}*/