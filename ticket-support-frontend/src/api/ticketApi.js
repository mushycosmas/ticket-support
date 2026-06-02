import api from "./axios";

// ----------------------
// TICKETS CRUD
// ----------------------
export const getTickets = () =>
    api.get("/tickets/tickets/");

export const getTicket = (id) =>
    api.get(`/tickets/tickets/${id}/`);

export const createTicket = (data) =>
    api.post("/tickets/tickets/", data);

export const updateTicket = (id, data) =>
    api.patch(`/tickets/tickets/${id}/`, data);

export const deleteTicket = (id) =>
    api.delete(`/tickets/tickets/${id}/`);

// ----------------------
// TICKET ACTIONS
// ----------------------
export const resolveTicket = (id) =>
    api.post(`/tickets/tickets/${id}/resolve/`);

export const closeTicket = (id) =>
    api.post(`/tickets/tickets/${id}/close/`);



export const assignTicket = (id, data) =>
    api.post(`/tickets/tickets/${id}/assign/`, data);


export const getMyTickets = () =>
    api.get("/tickets/tickets/?filter=my");

export const getAssignedTickets = () =>
    api.get("/tickets/tickets/?filter=assigned");

export const getUnassignedTickets = () =>
    api.get("/tickets/tickets/?filter=unassigned");

export const getClosedTickets = () =>
    api.get("/tickets/tickets/?filter=closed");