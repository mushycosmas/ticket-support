import React, { useState } from "react";
import { Table, Badge, Form, Row, Col, Card } from "react-bootstrap";

const SystemLogs = () => {
  const [search, setSearch] = useState("");

  const [logs] = useState([
    {
      id: 1,
      level: "info",
      message: "User admin logged in",
      date: "2026-06-01 10:30",
    },
    {
      id: 2,
      level: "warning",
      message: "Ticket #123 not assigned",
      date: "2026-06-01 11:00",
    },
    {
      id: 3,
      level: "error",
      message: "Database connection failed",
      date: "2026-06-01 12:10",
    },
    {
      id: 4,
      level: "info",
      message: "New ticket created",
      date: "2026-06-02 09:15",
    },
  ]);

  const getBadge = (level) => {
    switch (level) {
      case "info":
        return "primary";
      case "warning":
        return "warning";
      case "error":
        return "danger";
      default:
        return "secondary";
    }
  };

  const filteredLogs = logs.filter((log) =>
    log.message.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="container-fluid p-4">
      <h3 className="mb-3">System Logs</h3>

      {/* Filter */}
      <Card className="mb-3 shadow-sm">
        <Card.Body>
          <Row>
            <Col md={6}>
              <Form.Control
                type="text"
                placeholder="Search logs..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </Col>
          </Row>
        </Card.Body>
      </Card>

      {/* Logs Table */}
      <Card className="shadow-sm">
        <Card.Body>
          <Table striped hover responsive>
            <thead>
              <tr>
                <th>#</th>
                <th>Level</th>
                <th>Message</th>
                <th>Date</th>
              </tr>
            </thead>

            <tbody>
              {filteredLogs.length > 0 ? (
                filteredLogs.map((log, index) => (
                  <tr key={log.id}>
                    <td>{index + 1}</td>
                    <td>
                      <Badge bg={getBadge(log.level)}>
                        {log.level.toUpperCase()}
                      </Badge>
                    </td>
                    <td>{log.message}</td>
                    <td>{log.date}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="4" className="text-center text-muted">
                    No logs found
                  </td>
                </tr>
              )}
            </tbody>
          </Table>
        </Card.Body>
      </Card>
    </div>
  );
};

export default SystemLogs;