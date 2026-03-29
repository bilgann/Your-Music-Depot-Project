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
                <h2>{title}</h2>
                <form onSubmit={onSubmit}>
                    {children}
                    <div className="modal-buttons">
                        <button type="button" onClick={onClose}>Cancel</button>
                        <button type="submit" disabled={saving}>
                            {saving ? "Saving..." : submitLabel}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
