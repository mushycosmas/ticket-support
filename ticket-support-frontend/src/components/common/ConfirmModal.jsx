import React from "react";
import { Modal, Button } from "react-bootstrap";

const ConfirmModal = ({ show, onHide, title, message, onConfirm }) => {
    return (
        <Modal show={show} onHide={onHide} centered>

            <Modal.Header closeButton>
                <Modal.Title>{title || "Confirm Action"}</Modal.Title>
            </Modal.Header>

            <Modal.Body>
                {message || "Are you sure you want to continue?"}
            </Modal.Body>

            <Modal.Footer>
                <Button variant="secondary" onClick={onHide}>
                    Cancel
                </Button>

                <Button
                    variant="danger"
                    onClick={() => {
                        onConfirm();
                        onHide();
                    }}
                >
                    Yes, Delete
                </Button>
            </Modal.Footer>

        </Modal>
    );
};

export default ConfirmModal;