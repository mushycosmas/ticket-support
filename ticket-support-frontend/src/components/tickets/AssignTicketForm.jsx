import React, { useEffect, useState } from "react";
import { Form, Button, Spinner } from "react-bootstrap";
import { assignTicket } from "../../api/ticketApi";
import { getUsers } from "../../api/userApi";

const AssignTicketForm = ({ ticket, ticketId, onSuccess }) => {

    const [agents, setAgents] = useState([]);
    const [agentId, setAgentId] = useState("");
    const [loading, setLoading] = useState(false);

    // =====================
    // LOAD TEAM MEMBERS ONLY
    // =====================
    useEffect(() => {
        const loadTeamAgents = async () => {
            try {
                const res = await getUsers();

                // STEP 1: get ticket team
                const teamId = ticket?.team;

                // STEP 2: filter agents inside same team
                const teamAgents = res.data.filter(
                    user =>
                        user.role === "AGENT" &&
                        user.team === teamId
                );

                setAgents(teamAgents);

            } catch (err) {
                console.error("Failed to load team agents", err);
            }
        };

        if (ticket?.team) {
            loadTeamAgents();
        }

    }, [ticket]);

    // =====================
    // ASSIGN
    // =====================
    const handleAssign = async () => {

        if (!agentId) return;

        try {
            setLoading(true);

            await assignTicket(ticketId, {
                assigned_to: agentId,
                status: "IN_PROGRESS"
            });

            setAgentId("");
            onSuccess();

        } catch (err) {
            console.error("Assignment failed", err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="mt-3">

            <Form.Label>Assign Agent (Team Only)</Form.Label>

            <div className="d-flex gap-2">

                {/* AGENT SELECT */}
                <Form.Select
                    value={agentId}
                    onChange={(e) => setAgentId(e.target.value)}
                >
                    <option value="">-- Select Agent --</option>

                    {agents.map(agent => (
                        <option key={agent.id} value={agent.id}>
                            {agent.first_name} {agent.last_name}
                        </option>
                    ))}
                </Form.Select>

                {/* BUTTON */}
                <Button
                    onClick={handleAssign}
                    disabled={loading}
                >
                    {loading ? <Spinner size="sm" /> : "Assign"}
                </Button>

            </div>
        </div>
    );
};

export default AssignTicketForm;