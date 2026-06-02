import React, { useEffect, useState } from "react";
import { Modal, Button, Form } from "react-bootstrap";
import { createUser, updateUser, getTeams } from "../../api/userApi";

const UserFormModal = ({ show, onHide, user, onSuccess }) => {

    const [form, setForm] = useState({
        username: "",
        first_name: "",
        last_name: "",
        email: "",
        password: "",
        role: "AGENT",
        team: ""
    });

    const [teams, setTeams] = useState([]);

    useEffect(() => {
        getTeams().then(res => setTeams(res.data));
    }, []);

    useEffect(() => {
        if (user) {
            setForm(user);
        } else {
            setForm({
                username: "",
                first_name: "",
                last_name: "",
                email: "",
                password: "",
                role: "AGENT",
                team: ""
            });
        }
    }, [user]);

    const handleChange = (e) => {
        setForm({ ...form, [e.target.name]: e.target.value });
    };

    const handleSubmit = async () => {
        if (user) {
            await updateUser(user.id, form);
        } else {
            await createUser(form);
        }

        onSuccess();
        onHide();
    };

    return (
        <Modal show={show} onHide={onHide}>
            <Modal.Header closeButton>
                <Modal.Title>
                    {user ? "Edit User" : "Create User"}
                </Modal.Title>
            </Modal.Header>

            <Modal.Body>

                <Form>

                    <Form.Control
                        name="username"
                        placeholder="Username"
                        className="mb-2"
                        onChange={handleChange}
                        value={form.username}
                    />

                    <Form.Control
                        name="email"
                        placeholder="Email"
                        className="mb-2"
                        onChange={handleChange}
                        value={form.email}
                    />

                    <Form.Control
                        name="first_name"
                        placeholder="First Name"
                        className="mb-2"
                        onChange={handleChange}
                        value={form.first_name}
                    />

                    <Form.Control
                        name="last_name"
                        placeholder="Last Name"
                        className="mb-2"
                        onChange={handleChange}
                        value={form.last_name}
                    />

                    {!user && (
                        <Form.Control
                            name="password"
                            type="password"
                            placeholder="Password"
                            className="mb-2"
                            onChange={handleChange}
                            value={form.password}
                        />
                    )}

                    {/* ROLE */}
                    <Form.Select
                        name="role"
                        className="mb-2"
                        onChange={handleChange}
                        value={form.role}
                    >
                        <option value="AGENT">Agent</option>
                        <option value="TEAM_LEAD">Team Lead</option>
                        <option value="QA">QA</option>
                        <option value="MANAGER">Manager</option>
                        <option value="ADMIN">Admin</option>
                    </Form.Select>

                    {/* TEAM */}
                    <Form.Select
                        name="team"
                        onChange={handleChange}
                        value={form.team}
                    >
                        <option value="">Select Team</option>

                        {teams.map(t => (
                            <option key={t.id} value={t.id}>
                                {t.name}
                            </option>
                        ))}
                    </Form.Select>

                </Form>

            </Modal.Body>

            <Modal.Footer>
                <Button variant="secondary" onClick={onHide}>
                    Cancel
                </Button>

                <Button onClick={handleSubmit}>
                    Save
                </Button>
            </Modal.Footer>
        </Modal>
    );
};

export default UserFormModal;