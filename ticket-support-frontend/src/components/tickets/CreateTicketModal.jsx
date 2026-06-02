import React, { useEffect, useState } from "react";
import { Modal, Form, Button, Spinner } from "react-bootstrap";
import { createTicket } from "../../api/ticketApi";
import { getTeams } from "../../api/teamApi";

const CreateTicketModal = ({ show, onHide, onSuccess }) => {

    const [loading, setLoading] = useState(false);
    const [teams, setTeams] = useState([]);

    const [formData, setFormData] = useState({
        customer_name: "",
        customer_contact: "",
        channel: "WEB",
        title: "",
        description: "",
        priority: "MEDIUM",
        team: ""
    });

    // ======================
    // LOAD TEAMS
    // ======================
    useEffect(() => {
        const loadTeams = async () => {
            try {
                const res = await getTeams();
                setTeams(res.data);
            } catch (err) {
                console.error("Failed to load teams", err);
            }
        };

        if (show) loadTeams();
    }, [show]);

    // ======================
    // HANDLE INPUT CHANGE
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
        try {
            setLoading(true);

            await createTicket(formData);

            setFormData({
                customer_name: "",
                customer_contact: "",
                channel: "WEB",
                title: "",
                description: "",
                priority: "MEDIUM",
                team: ""
            });

            onSuccess();
            onHide();

        } catch (error) {
            console.error("Ticket creation failed", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Modal show={show} onHide={onHide} size="lg">

            <Modal.Header closeButton>
                <Modal.Title>Create Ticket</Modal.Title>
            </Modal.Header>

            <Modal.Body>

                <Form>

                    {/* CUSTOMER */}
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

                    {/* CHANNEL */}
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
                        <option value="WALKIN">WALK-IN</option>
                    </Form.Select>

                    {/* TITLE */}
                    <Form.Control
                        className="mb-2"
                        name="title"
                        placeholder="Title"
                        value={formData.title}
                        onChange={handleChange}
                    />

                    {/* DESCRIPTION */}
                    <Form.Control
                        as="textarea"
                        rows={3}
                        name="description"
                        placeholder="Description"
                        value={formData.description}
                        onChange={handleChange}
                    />

                    {/* PRIORITY */}
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

                    {/* TEAM ASSIGNMENT (🔥 NEW IMPORTANT FIELD) */}
                    <Form.Select
                        className="mt-2"
                        name="team"
                        value={formData.team}
                        onChange={handleChange}
                    >
                        <option value="">-- Select Team --</option>

                        {teams.map(team => (
                            <option key={team.id} value={team.id}>
                                {team.name}
                            </option>
                        ))}
                    </Form.Select>

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