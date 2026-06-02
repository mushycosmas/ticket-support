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

    // ======================
    // HANDLE INPUT
    // ======================
    const handleChange = (e) => {
        setForm((prev) => ({
            ...prev,
            [e.target.name]: e.target.value
        }));
    };

    // ======================
    // LOGIN SUBMIT
    // ======================
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
            if (user.role === "ADMIN") {
                navigate("/admin/users", { replace: true });

            } else if (user.role === "MANAGER") {
                navigate("/dashboard", { replace: true });

            } else if (user.role === "TEAM_LEAD") {
                navigate("/tickets", { replace: true });

            } else if (user.role === "AGENT") {
                navigate("/tickets", { replace: true });

            } else if (user.role === "CUSTOMER") {
                navigate("/tickets", { replace: true });

            } else {
                navigate("/dashboard", { replace: true });
            }

        } catch (err) {
            console.error("Login failed:", err);
            setError("Invalid username or password");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="d-flex justify-content-center align-items-center vh-100">

            <Card style={{ width: "400px" }} className="p-4 shadow-sm">

                <h4 className="text-center mb-3">Login</h4>

                {error && (
                    <Alert variant="danger">
                        {error}
                    </Alert>
                )}

                <Form onSubmit={handleSubmit}>

                    <Form.Group className="mb-2">
                        <Form.Control
                            name="username"
                            placeholder="Username"
                            value={form.username}
                            onChange={handleChange}
                        />
                    </Form.Group>

                    <Form.Group className="mb-3">
                        <Form.Control
                            type="password"
                            name="password"
                            placeholder="Password"
                            value={form.password}
                            onChange={handleChange}
                        />
                    </Form.Group>

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