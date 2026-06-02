import React, { useState } from "react";
import { Form, Button } from "react-bootstrap";
import { assignTicket } from "../../api/ticketApi";

const AssignTicketForm = ({ ticketId, onSuccess }) => {

    const [agent, setAgent] = useState("");

    const handleAssign = async () => {
        if (!agent) return;

        await assignTicket(ticketId, agent);
        setAgent("");
        onSuccess();
    };

    return (
        <div className="d-flex gap-2 mt-3">

            <Form.Control
                placeholder="Assign Agent Name"
                value={agent}
                onChange={(e) => setAgent(e.target.value)}
            />

            <Button onClick={handleAssign}>
                Assign
            </Button>

        </div>
    );
};

export default AssignTicketForm;