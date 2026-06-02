import React, { useState } from "react";
import { Form, Button, Card, Row, Col, Alert } from "react-bootstrap";

const Settings = () => {
  const [settings, setSettings] = useState({
    systemName: "Ticket Support System",
    supportEmail: "support@company.com",
    autoAssignTickets: true,
    allowGuestTickets: false,
    ticketPrefix: "TKT",
    maxUploadSize: 5,
  });

  const [saved, setSaved] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;

    setSettings({
      ...settings,
      [name]: type === "checkbox" ? checked : value,
    });

    setSaved(false);
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // 👉 Replace with API call later
    console.log("Saved settings:", settings);

    setSaved(true);
  };

  return (
    <div className="container-fluid p-4">
      <h3 className="mb-3">System Settings</h3>

      {saved && <Alert variant="success">Settings saved successfully!</Alert>}

      <Form onSubmit={handleSubmit}>
        <Row>
          {/* LEFT SIDE */}
          <Col md={6}>
            <Card className="mb-3 shadow-sm">
              <Card.Body>
                <h5>General Settings</h5>

                <Form.Group className="mb-3">
                  <Form.Label>System Name</Form.Label>
                  <Form.Control
                    type="text"
                    name="systemName"
                    value={settings.systemName}
                    onChange={handleChange}
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Support Email</Form.Label>
                  <Form.Control
                    type="email"
                    name="supportEmail"
                    value={settings.supportEmail}
                    onChange={handleChange}
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Ticket Prefix</Form.Label>
                  <Form.Control
                    type="text"
                    name="ticketPrefix"
                    value={settings.ticketPrefix}
                    onChange={handleChange}
                  />
                </Form.Group>
              </Card.Body>
            </Card>
          </Col>

          {/* RIGHT SIDE */}
          <Col md={6}>
            <Card className="mb-3 shadow-sm">
              <Card.Body>
                <h5>Ticket Configuration</h5>

                <Form.Group className="mb-3">
                  <Form.Check
                    type="switch"
                    label="Auto Assign Tickets"
                    name="autoAssignTickets"
                    checked={settings.autoAssignTickets}
                    onChange={handleChange}
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Check
                    type="switch"
                    label="Allow Guest Tickets"
                    name="allowGuestTickets"
                    checked={settings.allowGuestTickets}
                    onChange={handleChange}
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Max Upload Size (MB)</Form.Label>
                  <Form.Control
                    type="number"
                    name="maxUploadSize"
                    value={settings.maxUploadSize}
                    onChange={handleChange}
                  />
                </Form.Group>
              </Card.Body>
            </Card>
          </Col>
        </Row>

        <Button type="submit" variant="primary">
          Save Settings
        </Button>
      </Form>
    </div>
  );
};

export default Settings;