import Button from "@/components/ui/button";
import DataTable from "@/components/ui/data_table";
import type { Credential } from "@/features/instructors/api/instructor_detail";

interface Props {
    credentials: Credential[];
    onAdd: () => void;
    onDelete: (credentialId: string) => void;
}

function renderProficiencies(credential: Credential) {
    if (!credential.proficiencies?.length) return "--";
    return credential.proficiencies
        .map((item) => `${item.name} (${item.min_level} to ${item.max_level})`)
        .join(", ");
}

export default function InstructorCredentialsTab({ credentials, onAdd, onDelete }: Props) {
    return (
        <>
            <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 16 }}>
                <Button variant="primary" onClick={onAdd}>Add Credential</Button>
            </div>
            <DataTable
                loading={false}
                error={null}
                data={credentials}
                emptyMessage="No credentials recorded for this instructor."
                getKey={(credential) => credential.credential_id}
                columns={[
                    { header: "Type", render: (credential) => credential.credential_type },
                    { header: "Proficiencies", render: renderProficiencies },
                    { header: "Valid From", render: (credential) => credential.valid_from || "--" },
                    { header: "Valid Until", render: (credential) => credential.valid_until || "--" },
                ]}
                onDelete={(credential) => onDelete(credential.credential_id)}
            />
        </>
    );
}