import Button from "./button";

interface ModalProps {
    title: string;
    onClose: () => void;
    onSubmit: (e: React.FormEvent) => void;
    submitLabel?: string;
    saving?: boolean;
    children: React.ReactNode;
}

export default function Modal({ title, onClose, onSubmit, submitLabel = "Save", saving = false, children }: ModalProps) {
    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header"><h2>{title}</h2></div>
                <form onSubmit={onSubmit}>
                    {children}
                    <div className="modal-footer">
                        <Button variant="secondary" onClick={onClose}>Cancel</Button>
                        <Button variant="primary" type="submit" disabled={saving}>
                            {saving ? "Saving..." : submitLabel}
                        </Button>
                    </div>
                </form>
            </div>
        </div>
    );
}
