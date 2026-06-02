import React, { useEffect, useState } from "react";
import { Form, Button, Spinner } from "react-bootstrap";

import { assignTicket } from "../../api/ticketApi";
import { getUsers } from "../../api/userApi";
import { getTeams } from "../../api/teamApi";

const AssignTicketForm = ({ ticket, ticketId, onSuccess, onClose }) => {

    const user = JSON.parse(localStorage.getItem("user"));

    const [agents, setAgents] = useState([]);
    const [teams, setTeams] = useState([]);

    const [loading, setLoading] = useState(false);

    const [mode, setMode] = useState("agent");
    const [agentId, setAgentId] = useState("");
    const [teamId, setTeamId] = useState("");

    // =====================
    // LOAD USERS + FILTER
    // =====================
  useEffect(() => {

    const loadData = async () => {
        try {
            const [usersRes, teamsRes] = await Promise.all([
                getUsers(),
                getTeams()
            ]);

            const allUsers = usersRes.data;

            const ticketTeamId =
                ticket?.team_id ??
                ticket?.team?.id ??
                ticket?.team;

            if (!ticketTeamId) {
                console.warn("Ticket team is missing:", ticket);
                return;
            }

            const teamAgents = allUsers.filter(u =>
                u.role === "AGENT" &&
                Number(u.team_id) === Number(ticketTeamId)
            );

            setAgents(teamAgents);
            setTeams(teamsRes.data);

        } catch (err) {
            console.error("Failed loading assign data", err);
        }
    };

    if (ticket) {
        loadData();
    }

}, [ticket]);

    // =====================
    // ASSIGN HANDLER
    // =====================
    const handleAssign = async () => {

        if (loading) return;

        let payload = {};

        try {
            setLoading(true);

            // =====================
            // ADMIN
            // =====================
            if (user.role === "ADMIN") {

                if (mode === "team") {
                    if (!teamId) return alert("Select team");

                    payload = {
                        team_id: Number(teamId)
                    };

                } else {
                    if (!agentId) return alert("Select agent");

                    payload = {
                        assigned_to: Number(agentId)
                    };
                }
            }

            // =====================
            // TEAM LEAD (ONLY AGENT)
            // =====================
            if (user.role === "TEAM_LEAD") {

                if (!agentId) return alert("Select agent");

                payload = {
                    assigned_to: Number(agentId)
                };
            }

            await assignTicket(ticketId, payload);

            setAgentId("");
            setTeamId("");

            onSuccess?.();
            onClose?.();

        } catch (err) {
            console.error(err.response?.data || err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="mt-3">

            <h6 className="mb-2">Assign Ticket</h6>

            {/* ADMIN MODE SWITCH */}
            {user.role === "ADMIN" && (
                <Form.Select
                    className="mb-2"
                    value={mode}
                    onChange={(e) => setMode(e.target.value)}
                >
                    <option value="agent">Assign to Agent</option>
                    <option value="team">Assign to Team</option>
                </Form.Select>
            )}

            {/* TEAM SELECT (ADMIN ONLY) */}
            {user.role === "ADMIN" && mode === "team" && (
                <Form.Select
                    className="mb-2"
                    value={teamId}
                    onChange={(e) => setTeamId(e.target.value)}
                >
                    <option value="">Select Team</option>
                    {teams.map(team => (
                        <option key={team.id} value={team.id}>
                            {team.name}
                        </option>
                    ))}
                </Form.Select>
            )}

            {/* AGENT SELECT (ADMIN + TEAM LEAD FILTERED) */}
            {(mode === "agent" || user.role === "TEAM_LEAD") && (
                <Form.Select
                    className="mb-2"
                    value={agentId}
                    onChange={(e) => setAgentId(e.target.value)}
                >
                    <option value="">Select Agent</option>

                    {agents.map(agent => (
                        <option key={agent.id} value={agent.id}>
                            {agent.first_name} {agent.last_name}
                        </option>
                    ))}
                </Form.Select>
            )}

            {/* BUTTON */}
            <Button
                onClick={handleAssign}
                disabled={loading}
            >
                {loading ? <Spinner size="sm" /> : "Assign Ticket"}
            </Button>

        </div>
    );
};

export default AssignTicketForm;