const http = require('http');

let registeredUsers = {};
let eventRegistrations = new Set();
let eventRegistrationCounts = {};
const EVENT_CAPACITY = 100;

// Pre-seed a user for the login happy path test
registeredUsers["user@example.com"] = { name: "Existing User", password: "password123" };

const server = http.createServer((req, res) => {
    res.setHeader('Content-Type', 'application/json');

    let body = '';
    req.on('data', chunk => {
        body += chunk.toString();
    });

    req.on('end', () => {
        const parsedBody = body ? JSON.parse(body) : {};
        const authHeader = req.headers['authorization'];

        // Helper to check token validity
        const isAuthorized = () => {
            if (!authHeader || !authHeader.startsWith('Bearer ')) return 'missing';
            const token = authHeader.substring(7);
            if (token === 'invalid.malformed.token') return 'malformed';
            return 'valid';
        };

        const handleAuthError = (status) => {
            if (status === 'missing') {
                res.writeHead(401);
                res.end(JSON.stringify({ error: "Unauthorized: Missing token" }));
                return true;
            }
            if (status === 'malformed') {
                res.writeHead(401);
                res.end(JSON.stringify({ error: "Unauthorized: Invalid or malformed token" }));
                return true;
            }
            return false;
        };

        // --- POST /api/register ---
        if (req.method === 'POST' && req.url === '/api/register') {
            if (!parsedBody.name || !parsedBody.email || !parsedBody.password) {
                res.writeHead(400);
                res.end(JSON.stringify({ error: "Missing required fields: name, email, and password are required" }));
                return;
            }
            if (parsedBody.email in registeredUsers) {
                res.writeHead(409);
                res.end(JSON.stringify({ error: "Email already registered" }));
                return;
            }
            registeredUsers[parsedBody.email] = { name: parsedBody.name, password: parsedBody.password };
            res.writeHead(201);
            res.end(JSON.stringify({ message: "User registered successfully", userId: "user_12345" }));
            return;
        }

        // --- POST /api/login ---
        if (req.method === 'POST' && req.url === '/api/login') {
            if (!parsedBody.email || !parsedBody.password) {
                res.writeHead(400);
                res.end(JSON.stringify({ error: "Email and password are required" }));
                return;
            }
            const user = registeredUsers[parsedBody.email];
            if (!user || user.password !== parsedBody.password) {
                res.writeHead(401);
                res.end(JSON.stringify({ error: "Invalid credentials" }));
                return;
            }
            res.writeHead(200);
            res.end(JSON.stringify({ token: "mocked_jwt_token_abc123" }));
            return;
        }

        // --- GET /api/events ---
        if (req.method === 'GET' && req.url === '/api/events') {
            if (handleAuthError(isAuthorized())) return;
            res.writeHead(200);
            res.end(JSON.stringify({
                events: [
                    {
                        id: "event_999",
                        title: "MSAI Tech Keynote",
                        description: "Annual keynote speech on the future of AI workflows",
                        date: "2026-07-08T10:00:00Z",
                        location: "Virtual",
                        capacity: 100,
                        registered: 42
                    }
                ]
            }));
            return;
        }

        // --- POST /api/events/register ---
        if (req.method === 'POST' && req.url === '/api/events/register') {
            if (handleAuthError(isAuthorized())) return;
            if (!parsedBody.eventId) {
                res.writeHead(400);
                res.end(JSON.stringify({ error: "eventId is required" }));
                return;
            }
            if (eventRegistrations.has(parsedBody.eventId)) {
                res.writeHead(409);
                res.end(JSON.stringify({ error: "Already registered for this event" }));
                return;
            }
            if ((eventRegistrationCounts[parsedBody.eventId] || 0) >= EVENT_CAPACITY) {
                res.writeHead(422);
                res.end(JSON.stringify({ error: "Event is full" }));
                return;
            }
            eventRegistrations.add(parsedBody.eventId);
            eventRegistrationCounts[parsedBody.eventId] = (eventRegistrationCounts[parsedBody.eventId] || 0) + 1;
            res.writeHead(200);
            res.end(JSON.stringify({ message: "Successfully registered for event", registrationId: "reg_xyz789" }));
            return;
        }

        // --- POST /api/payment ---
        if (req.method === 'POST' && req.url === '/api/payment') {
            if (handleAuthError(isAuthorized())) return;
            if (!parsedBody.registrationId || parsedBody.amount === undefined || !parsedBody.currency || !parsedBody.paymentMethod) {
                res.writeHead(400);
                res.end(JSON.stringify({ error: "Missing required payment fields" }));
                return;
            }
            if (parsedBody.amount <= 0) {
                res.writeHead(422);
                res.end(JSON.stringify({ error: "Invalid amount: must be greater than zero" }));
                return;
            }
            res.writeHead(200);
            res.end(JSON.stringify({ message: "Payment successful", transactionId: "tx_pay12345" }));
            return;
        }

        // --- GET /api/registrations ---
        if (req.method === 'GET' && req.url === '/api/registrations') {
            if (handleAuthError(isAuthorized())) return;
            res.writeHead(200);
            res.end(JSON.stringify({
                registrations: [
                    {
                        registrationId: "reg_xyz789",
                        eventId: "event_999",
                        eventTitle: "MSAI Tech Keynote",
                        registeredAt: "2026-07-08T01:00:00Z",
                        paymentStatus: "paid"
                    }
                ]
            }));
            return;
        }

        // 404 Not Found
        res.writeHead(404);
        res.end(JSON.stringify({ error: "Not Found" }));
    });
});

const PORT = 3000;
server.listen(PORT, () => {
    console.log(`Mock server running at http://localhost:${PORT}`);
});
