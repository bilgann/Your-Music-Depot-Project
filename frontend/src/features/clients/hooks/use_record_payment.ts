import { useState } from "react";
import { recordClientPayment } from "@/features/clients/api/client";

export function useRecordPayment(clientId: string, refresh: () => Promise<void>) {
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
        } catch { alert("Payment failed."); }
        finally { setPaying(false); }
    }

    return { showPayModal, setShowPayModal, payAmount, setPayAmount, payMethod, setPayMethod, paying, handlePay };
}
