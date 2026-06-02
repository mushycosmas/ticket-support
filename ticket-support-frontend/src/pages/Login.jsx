import React, { useState } from "react";
import { Form, Button, Card, Spinner, Alert } from "react-bootstrap";
import { loginUser } from "../api/authApi";
import { useNavigate } from "react-router-dom";

const Login = () => {

    const [form, setForm] = useState({
        username: "",
        password: ""
    });

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const navigate = useNavigate();

    const handleChange = (e) => {
        setForm({
            ...form,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            setLoading(true);
            setError("");

            const res = await loginUser(form);

            const { access, user } = res.data;

            // ======================
            // STORE AUTH DATA
            // ======================
            localStorage.setItem("token", access);
            localStorage.setItem("user", JSON.stringify(user));

            // ======================
            // ROLE-BASED ROUTING
            // ======================
            switch (user.role) {

                case "ADMIN":
                    navigate("/admin/users");
                    break;

                case "MANAGER":
                    navigate("/dashboard");
                    break;

                case "TEAM_LEAD":
                    navigate("/tickets");
                    break;

                case "AGENT":
                    navigate("/tickets");
                    break;

                case "CUSTOMER":
                    navigate("/tickets");
                    break;

                default:
                    navigate("/dashboard");
            }

        } catch (err) {
            console.error("Login failed", err);
            setError("Invalid username or password");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="d-flex justify-content-center align-items-center" style={{ height: "100vh" }}>

            <Card style={{ width: "400px" }} className="p-3">

                <h4 className="text-center mb-3">Login</h4>

                {error && <Alert variant="danger">{error}</Alert>}

                <Form onSubmit={handleSubmit}>

                    <Form.Control
                        className="mb-2"
                        name="username"
                        placeholder="Username"
                        onChange={handleChange}
                        value={form.username}
                    />

                    <Form.Control
                        className="mb-3"
                        type="password"
                        name="password"
                        placeholder="Password"
                        onChange={handleChange}
                        value={form.password}
                    />

                    <Button
                        type="submit"
                        className="w-100"
                        disabled={loading}
                    >
                        {loading ? <Spinner size="sm" /> : "Login"}
                    </Button>

                </Form>

            </Card>

        </div>
    );
};

export default Login;