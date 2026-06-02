import React, { useEffect, useState } from "react";
import { Form, Button, Spinner } from "react-bootstrap";
import { assignTicket } from "../../api/ticketApi";
import { getUsers } from "../../api/userApi";

const AssignTicketForm = ({ ticket, ticketId, onSuccess }) => {

    const [agents, setAgents] = useState([]);
    const [agentId, setAgentId] = useState("");
    const [loading, setLoading] = useState(false);

    // =====================
    // LOAD TEAM AGENTS
    // =====================
    useEffect(() => {

        const loadTeamAgents = async () => {

            try {
                const res = await getUsers();

                const teamId = ticket?.team;

                const teamAgents = res.data.filter(user =>
                    user.role === "AGENT" &&
                    Number(user.team) === Number(teamId)
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

    console.log("agentId =", agentId);

    if (!agentId) {
        alert("Please select an agent");
        return;
    }

    try {
        setLoading(true);

        await assignTicket(ticketId, {
            assigned_to: Number(agentId)
        });

        onSuccess();

    } catch (err) {
        console.error(err.response?.data);
    } finally {
        setLoading(false);
    }
};
    return (
        <div className="mt-3">

            <Form.Label>Assign Agent (Team Only)</Form.Label>

            <div className="d-flex gap-2">

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