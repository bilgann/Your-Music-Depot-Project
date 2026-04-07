import { useState } from "react";
import { recordClientPayment } from "@/features/clients/api/client";
import { useToast } from "@/components/ui/toast";

export function useRecordPayment(clientId: string, refresh: () => Promise<void>) {
    const { toast } = useToast();
    const [showPayModal, setShowPayModal] = useState(false);
    const [payAmount, setPayAmount] = useState("");
    const [payMethod, setPayMethod] = useState("cash");
    const [paying, setPaying] = useState(false);

    async function handlePay(e: React.FormEvent) {
        e.preventDefault();
        setPaying(true);
        try {
            await recordClientPayment(clientId, { amount: parseFloat(payAmount), payment_method: payMethod });
            setShowPayModal(false);
            setPayAmount("");
            await refresh();
        } catch { toast("Payment failed.", "error"); }
        finally { setPaying(false); }
    }

    return { showPayModal, setShowPayModal, payAmount, setPayAmount, payMethod, setPayMethod, paying, handlePay };
}
