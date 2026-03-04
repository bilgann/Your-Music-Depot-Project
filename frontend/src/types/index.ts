/* 

Setting tpyes for the dropdown's + form field's
- Julien
*/

export interface FormField {
    name: string;
    type: 'text' | 'number' | 'dropdown';
    label: string;
    placeholder?: string;
    fetchUrl?: string;
    labelKey?: string;
    valueKey?: string;
}

export interface FormConfig {
    title: string;
    fields: FormField[];
    endpoint: string;
}

export interface FormData {
    [key: string]: any;
}

export interface DropdownOption {
    [key: string]: any;
}