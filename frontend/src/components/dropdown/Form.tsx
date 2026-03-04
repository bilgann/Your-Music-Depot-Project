/* 

This will be the Form Component holding the deafult function
to create the different forms we will need

Hope this is helpful :)

Will also contain validation :)

- Julien

How to call it/ Use it:

<ModalForm
    isOpen={isModalOpen}
    onClose={() => setIsModalOpen(false)}
    title={currentFormConfig.title}
    fields={currentFormConfig.fields}
    onSubmit={handleFormSubmit}
    isLoading={false}
/>

*/

import React, { useState, useEffect } from 'react';
import { FormField, FormData, DropdownOption } from '@/types';
// import '.css';

interface FormProps {
    isOpen: boolean;
    onClose: () => void;
    title: string;
    fields: FormField [];
    onSubmit: (data: FormData) => Promise<void>;
    initialData?: FormData;
    isLoading?: boolean;
} 

const Form: React.FC<FormProps> = ({
    isOpen,
    onClose,
    title,
    fields,
    onSubmit,
    initialData = {},
    isLoading = false
}) => {

    const [formData, setFormData] = useState<FormData>(initialData);
    const [errors, setErrors] = useState<Record<string, string>>({});

    useEffect(() => {
        setFormData(initialData);
    }, [initialData]);

    if (!isOpen) return null;

    const handleFieldChange = (fieldName: string, value: any) => {
        setFormData(prev => ({
            ...prev,
            [fieldName]: value
        }));

        if (errors[fieldName]) {
            setErrors(prev => ({
                ...prev,
                [fieldName]: ''
            }));
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await onSubmit(formData);
            onClose();
        } catch (error) {
            console.log('Form Submission error:', error)
        }
    
    };

    //TODO: Create renderField function for the form field to return the Dropdowns

    //TODO: Create both text and number return case statements

    //TODO: Create return Statement

}

export default Form;