import InfoCard from "@/components/ui/info_card";
import type { Client } from "@/features/clients/api/client";

interface Props {
    client: Client;
}

export default function ClientInfoCard({ client }: Props) {
    return (
        <InfoCard rows={[
            { label: "Email",   value: client.person.email || "--" },
            { label: "Phone",   value: client.person.phone || "--" },
            { label: "Credits", value: `$${Number(client.credits ?? 0).toFixed(2)}`, className: "client-credits" },
        ]} />
    );
}
