import React, { useEffect, useState } from "react";
import { Modal, Button, Form } from "react-bootstrap";

import {
    createUser,
    updateUser,
    getTeams
} from "../../api/userApi";

import { getRegions } from "../../api/locationApi";

const UserFormModal = ({ show, onHide, user, onSuccess }) => {

    // =========================
    // FORM STATE
    // =========================
    const [form, setForm] = useState({
        username: "",
        first_name: "",
        last_name: "",
        email: "",
        password: "",
        role: "AGENT",
        team: "",
        region: ""
    });

    const [teams, setTeams] = useState([]);
    const [regions, setRegions] = useState([]);

    // =========================
    // LOAD TEAMS
    // =========================
    useEffect(() => {
        getTeams()
            .then(res => setTeams(res.data))
            .catch(err => console.error("Failed to load teams", err));
    }, []);

    // =========================
    // LOAD REGIONS
    // =========================
    useEffect(() => {
        getRegions()
            .then(res => setRegions(res.data))
            .catch(err => console.error("Failed to load regions", err));
    }, []);

    // =========================
    // FILL FORM FOR EDIT / RESET FOR CREATE
    // =========================
    useEffect(() => {
        if (user) {
            setForm({
                username: user.username || "",
                first_name: user.first_name || "",
                last_name: user.last_name || "",
                email: user.email || "",
                password: "",
                role: user.role || "AGENT",
                team: user.team || "",
                region: user.region || ""
            });
        } else {
            setForm({
                username: "",
                first_name: "",
                last_name: "",
                email: "",
                password: "",
                role: "AGENT",
                team: "",
                region: ""
            });
        }
    }, [user]);

    // =========================
    // HANDLE INPUT CHANGE
    // =========================
    const handleChange = (e) => {
        setForm({
            ...form,
            [e.target.name]: e.target.value
        });
    };

    // =========================
    // SUBMIT
    // =========================
    const handleSubmit = async () => {

        const payload = {
            ...form,
            region: form.region
        };

        try {
            if (user) {
                await updateUser(user.id, payload);
            } else {
                await createUser(payload);
            }

            onSuccess();
            onHide();

        } catch (err) {
            console.error("User save failed", err);
            alert("Failed to save user");
        }
    };

    return (
        <Modal show={show} onHide={onHide} centered>
            <Modal.Header closeButton>
                <Modal.Title>
                    {user ? "Edit User" : "Create User"}
                </Modal.Title>
            </Modal.Header>

            <Modal.Body>
                <Form>

                    {/* USERNAME */}
                    <Form.Control
                        name="username"
                        placeholder="Username"
                        className="mb-2"
                        onChange={handleChange}
                        value={form.username}
                    />

                    {/* EMAIL */}
                    <Form.Control
                        name="email"
                        placeholder="Email"
                        className="mb-2"
                        onChange={handleChange}
                        value={form.email}
                    />

                    {/* FIRST NAME */}
                    <Form.Control
                        name="first_name"
                        placeholder="First Name"
                        className="mb-2"
                        onChange={handleChange}
                        value={form.first_name}
                    />

                    {/* LAST NAME */}
                    <Form.Control
                        name="last_name"
                        placeholder="Last Name"
                        className="mb-2"
                        onChange={handleChange}
                        value={form.last_name}
                    />

                    {/* PASSWORD */}
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

                    {/* REGION (NEW) */}
                    <Form.Select
                        name="region"
                        className="mb-2"
                        onChange={handleChange}
                        value={form.region}
                    >
                        <option value="">Select Region</option>

                        {regions.map((r) => (
                            <option key={r.id} value={r.id}>
                                {r.name}
                            </option>
                        ))}
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