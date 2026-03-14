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
import Dropdown from './drop_down';
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

    const handleFieldChange = (fieldName: string, value: string | number) => {
        setFormData((prev: FormData) => ({
            ...prev,
            [fieldName]: value
        }));

        if (errors[fieldName]) {
            setErrors((prev: Record<string, string>) => ({
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

    const renderField = (field: FormField) => {
        switch (field.type) {

            case 'dropdown':
                return (
                    <div key={field.name} className='form-field'>
                        <label>{field.label}</label>
                        <Dropdown
                            fetchUrl={field.fetchUrl}
                            labelKey={field.labelKey}
                            valueKey={field.valueKey}
                            placeholder={field.placeholder}
                            value={formData[field.name]}
                            onChange={(value: string) => handleFieldChange(field.name, value)}
                        />
                        {errors[field.name] && (
                            <span className='error'>{errors[field.name]}</span>
                        )}
                    </div>
                );

            case 'text':
                return (
                    <div key={field.name} className='form-field'>
                        <label>{field.label}</label>
                        <input
                            type='text'
                            value={formData[field.name] || ''}
                            onChange={(e) => handleFieldChange(field.name, e.target.value)}
                            placeholder={field.placeholder}
                        />
                        {errors[field.name] && (
                            <span className='error'>{errors[field.name]}</span>
                        )}
                    </div>
                );

            case 'number':
                return (
                    <div key={field.name} className='form-field'>
                        <label>{field.label}</label>
                        <input
                            type='number'
                            value={formData[field.name] || ''}
                            onChange={(e) => handleFieldChange(field.name, e.target.value)}
                            placeholder={field.placeholder}
                        />
                        {errors[field.name] && (
                            <span className='error'>{errors[field.name]}</span>
                        )}
                    </div>
                );

            default:
                return null;
        }   
    }

    return (
        <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{title}</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-grid">
            {fields.map(renderField)}
          </div>
          
          <div className="modal-footer">
            <button type="button" onClick={onClose} className="btn btn-secondary">
              Cancel
            </button>
            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={isLoading}
            >
              Submit
            </button>
          </div>
        </form>
      </div>
    </div>
    );
}

export default Form;