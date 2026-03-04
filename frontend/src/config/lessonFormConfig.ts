/* 

Required to have a config for each of the forms we
will be building

- Julien

*/

import { FormField, FormConfig } from "@/types";

const lessonFields: FormField[] = [
    {
    name: 'title',
    type: 'text',
    label: 'Lesson Title',
    placeholder: 'Enter lesson title'
  },
  {
    name: 'duration',
    type: 'number',
    label: 'Duration (minutes)',
    placeholder: 'Enter duration'
  },
  {
    name: 'teacherId',
    type: 'dropdown',
    label: 'Teacher',
    fetchUrl: '/api/teachers',
    labelKey: 'name',
    valueKey: 'id'
  },
  {
    name: 'subjectId',
    type: 'dropdown',
    label: 'Subject',
    fetchUrl: '/api/subjects',
    labelKey: 'name',
    valueKey: 'id'
  }
];

const lessonFormConfig: FormConfig = {
  title: 'Add New Lesson',
  fields: lessonFields,
  endpoint: '/api/lessons'
};

export default lessonFormConfig;