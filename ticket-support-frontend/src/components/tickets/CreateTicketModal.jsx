import React, { useEffect, useState } from "react";
import { Modal, Form, Button, Spinner } from "react-bootstrap";

import { createTicket } from "../../api/ticketApi";
import { getTeams } from "../../api/teamApi";
import { getUsers } from "../../api/userApi";

const CreateTicketModal = ({ show, onHide, onSuccess }) => {

    const user = JSON.parse(localStorage.getItem("user"));

    const [loading, setLoading] = useState(false);
    const [teams, setTeams] = useState([]);
    const [agents, setAgents] = useState([]);

    const [mode, setMode] = useState("agent");

    const [formData, setFormData] = useState({
        customer_name: "",
        customer_contact: "",
        channel: "WEB",
        title: "",
        description: "",
        priority: "MEDIUM",
        team: "",
        assigned_to: ""
    });

    // ======================
    // RESET FORM
    // ======================
    useEffect(() => {
        if (show) {
            setFormData({
                customer_name: "",
                customer_contact: "",
                channel: "WEB",
                title: "",
                description: "",
                priority: "MEDIUM",
                team: "",
                assigned_to: ""
            });
            setMode("agent");
        }
    }, [show]);

    // ======================
    // LOAD TEAMS + USERS
    // ======================
    useEffect(() => {

        const loadData = async () => {
            try {
                const [teamsRes, usersRes] = await Promise.all([
                    getTeams(),
                    getUsers()
                ]);

                const allTeams = teamsRes.data || [];
                const allUsers = usersRes.data || [];

                setTeams(allTeams);

                // ======================
                // ROLE-BASED FILTER (FIXED)
                // ======================

                if (user.role === "TEAM_LEAD") {

                    const myTeamId = user.team;

                    const teamAgents = allUsers.filter(
                        u =>
                            u.role === "AGENT" &&
                            Number(u.team_id) === Number(myTeamId)
                    );

                    setAgents(teamAgents);

                    setFormData(prev => ({
                        ...prev,
                        team: myTeamId
                    }));
                }

                else {
                    // ADMIN sees all agents
                    setAgents(allUsers.filter(u => u.role === "AGENT"));
                }

            } catch (err) {
                console.error("Failed loading data", err);
            }
        };

        if (show) loadData();

    }, [show, user.role, user.team]);

    // ======================
    // HANDLE INPUT
    // ======================
    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    // ======================
    // SUBMIT
    // ======================
    const handleSubmit = async () => {

        if (!formData.customer_name || !formData.title) {
            alert("Customer name and title required");
            return;
        }

        let payload = {
            ...formData
        };

        // ======================
        // ADMIN LOGIC
        // ======================
        if (user.role === "ADMIN") {

            if (mode === "team") {
                payload.assigned_to = null;
            }

            if (mode === "agent" && !formData.assigned_to) {
                alert("Select agent");
                return;
            }
        }

        // ======================
        // TEAM LEAD LOGIC
        // ======================
        if (user.role === "TEAM_LEAD") {

            if (!formData.assigned_to) {
                alert("Select agent");
                return;
            }

            payload.team = user.team;
        }

        try {
            setLoading(true);

            await createTicket(payload);

            onSuccess?.();
            onHide?.();

        } catch (err) {
            console.error(err?.response?.data || err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Modal show={show} onHide={onHide} size="lg" centered>

            <Modal.Header closeButton>
                <Modal.Title>Create Ticket</Modal.Title>
            </Modal.Header>

            <Modal.Body>

                <Form>

                    <Form.Control
                        className="mb-2"
                        name="customer_name"
                        placeholder="Customer Name"
                        value={formData.customer_name}
                        onChange={handleChange}
                    />

                    <Form.Control
                        className="mb-2"
                        name="customer_contact"
                        placeholder="Contact"
                        value={formData.customer_contact}
                        onChange={handleChange}
                    />

                    <Form.Select
                        className="mb-2"
                        name="channel"
                        value={formData.channel}
                        onChange={handleChange}
                    >
                        <option value="WEB">WEB</option>
                        <option value="EMAIL">EMAIL</option>
                        <option value="PHONE">PHONE</option>
                        <option value="CHAT">CHAT</option>
                    </Form.Select>

                    <Form.Control
                        className="mb-2"
                        name="title"
                        placeholder="Title"
                        value={formData.title}
                        onChange={handleChange}
                    />

                    <Form.Control
                        as="textarea"
                        rows={3}
                        name="description"
                        placeholder="Description"
                        value={formData.description}
                        onChange={handleChange}
                    />

                    <Form.Select
                        className="mt-2"
                        name="priority"
                        value={formData.priority}
                        onChange={handleChange}
                    >
                        <option value="LOW">LOW</option>
                        <option value="MEDIUM">MEDIUM</option>
                        <option value="HIGH">HIGH</option>
                        <option value="CRITICAL">CRITICAL</option>
                    </Form.Select>

                    {/* ADMIN MODE SWITCH */}
                    {user.role === "ADMIN" && (
                        <Form.Select
                            className="mt-2"
                            value={mode}
                            onChange={(e) => setMode(e.target.value)}
                        >
                            <option value="agent">Assign to Agent</option>
                            <option value="team">Assign to Team</option>
                        </Form.Select>
                    )}

                    {/* AGENT SELECT */}
                    {(user.role === "TEAM_LEAD" ||
                        (user.role === "ADMIN" && mode === "agent")) && (
                        <Form.Select
                            className="mt-2"
                            name="assigned_to"
                            value={formData.assigned_to}
                            onChange={handleChange}
                        >
                            <option value="">Select Agent</option>

                            {agents.map(agent => (
                                <option key={agent.id} value={agent.id}>
                                    {agent.first_name} {agent.last_name}
                                </option>
                            ))}
                        </Form.Select>
                    )}

                    {/* TEAM SELECT (ADMIN ONLY) */}
                    {user.role === "ADMIN" && mode === "team" && (
                        <Form.Select
                            className="mt-2"
                            name="team"
                            value={formData.team}
                            onChange={handleChange}
                        >
                            <option value="">Select Team</option>

                            {teams.map(team => (
                                <option key={team.id} value={team.id}>
                                    {team.name}
                                </option>
                            ))}
                        </Form.Select>
                    )}

                </Form>

            </Modal.Body>

            <Modal.Footer>
                <Button variant="secondary" onClick={onHide}>
                    Cancel
                </Button>

                <Button
                    variant="primary"
                    onClick={handleSubmit}
                    disabled={loading}
                >
                    {loading ? <Spinner size="sm" /> : "Create Ticket"}
                </Button>
            </Modal.Footer>

        </Modal>
    );
};

export default CreateTicketModal;