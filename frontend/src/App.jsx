import React, { useState, useEffect, createContext, useContext } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  useNavigate,
} from "react-router-dom";
import "./App.css";

const API_URL = "http://localhost:9002";
const CREDENTIALS = { worker1: "pass1", manager1: "pass2" };

// — Auth boilerplate —
const AuthContext = createContext();
function useAuth() {
  return useContext(AuthContext);
}
function AuthProvider({ children }) {
  const [auth, setAuth] = useState({
    user: sessionStorage.getItem("user"),
    role: sessionStorage.getItem("role"),
  });
  const login = (u, r) => {
    sessionStorage.setItem("user", u);
    sessionStorage.setItem("role", r);
    setAuth({ user: u, role: r });
  };
  const logout = () => {
    sessionStorage.clear();
    setAuth({ user: null, role: null });
  };
  return (
    <AuthContext.Provider value={{ ...auth, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// — Route guard —
function Protected({ role, children }) {
  const auth = useAuth();
  if (!auth.user || auth.role !== role) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

// — Login Page —
function LoginPage() {
  const navigate = useNavigate();
  const auth = useAuth();
  const [userInput, setUserInput] = useState("");
  const [passInput, setPassInput] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (CREDENTIALS[userInput] === passInput) {
      const role = userInput.startsWith("worker") ? "worker" : "manager";
      auth.login(userInput, role);
      navigate(`/${role}`);
    } else {
      setError("Invalid credentials");
    }
  };

  return (
    <div className="page login-page">
      <div className="login-container">
        <form onSubmit={handleSubmit} className="card login-card">
          <h2>Sign In</h2>
          {error && <p className="error">{error}</p>}
          <input
            placeholder="Username"
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={passInput}
            onChange={(e) => setPassInput(e.target.value)}
            required
          />
          <button>Log In</button>
          <small className="creds">
            Worker: worker1 / pass1
            <br />
            Manager: manager1 / pass2
          </small>
        </form>
      </div>
    </div>
  );
}

// — Worker Dashboard —
function WorkerPage() {
  const { user, logout } = useAuth();
  const [date, setDate] = useState("");
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [sig, setSig] = useState("");
  const [shifts, setShifts] = useState([]);

  useEffect(() => {
    fetchChain();
  }, []);
  async function fetchChain() {
    const res = await fetch(`${API_URL}/chain`);
    setShifts(await res.json());
  }

  async function logShift(e) {
    e.preventDefault();
    await fetch(`${API_URL}/submit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: user,
        password: CREDENTIALS[user],
        date,
        shift_start: start,
        shift_end: end,
        worker_signature: sig,
      }),
    });
    fetchChain();
  }

  return (
    <div className="page dash-page">
      <div className="dashboard-container">
        <div className="topbar">
          <h2>Worker Dashboard</h2>
          <button onClick={logout}>Logout</button>
        </div>
        <div className="dash-grid">
          <form onSubmit={logShift} className="form-card card">
            <h3>Log a Shift</h3>
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              required
            />
            <input
              type="time"
              value={start}
              onChange={(e) => setStart(e.target.value)}
              required
            />
            <input
              type="time"
              value={end}
              onChange={(e) => setEnd(e.target.value)}
              required
            />
            <input
              placeholder="Your Signature"
              value={sig}
              onChange={(e) => setSig(e.target.value)}
              required
            />
            <button type="submit">Submit</button>
          </form>
          <div className="list-card card">
            <h3>My Shifts</h3>
            <ShiftList shifts={shifts} showApprove={false} />
          </div>
        </div>
      </div>
    </div>
  );
}

// — Manager Dashboard —
function ManagerPage() {
  const { logout } = useAuth();
  const [shifts, setShifts] = useState([]);

  useEffect(() => {
    fetchChain();
  }, []);
  async function fetchChain() {
    const res = await fetch(`${API_URL}/chain`);
    setShifts(await res.json());
  }
  async function decision(hash, idx, action) {
    await fetch(`${API_URL}/${action}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: "manager1",
        password: "pass2",
        block_hash: hash,
        tx_index: idx,
      }),
    });
    fetchChain();
  }

  return (
    <div className="page dash-page">
      <div className="dashboard-container">
        <div className="topbar">
          <h2>Manager Panel</h2>
          <button onClick={logout}>Logout</button>
        </div>
        <div className="dash-grid">
          <div className="list-card card">
            <h3>All Shifts</h3>
            <ShiftList
              shifts={shifts}
              showApprove={true}
              onApprove={(h, i) => decision(h, i, "approve")}
              onReject={(h, i) => decision(h, i, "reject")}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

// — Shared Shift List —
function ShiftList({ shifts, showApprove, onApprove, onReject }) {
  return (
    <ul className="shift-list">
      {shifts.map((b) =>
        b.transactions.map((tx, i) => (
          <li key={`${b.hash}-${i}`}>
            <span>
              #{b.index} {tx.date} {tx.shift_start}-{tx.shift_end}
            </span>
            <div>
              {showApprove && !tx.supervisor_signature && (
                <>
                  <button
                    className="btn-accept"
                    onClick={() => onApprove(b.hash, i)}
                  >
                    Approve
                  </button>
                  <button
                    className="btn-reject"
                    onClick={() => onReject(b.hash, i)}
                  >
                    Reject
                  </button>
                </>
              )}
              {tx.supervisor_signature && (
                <span className="status">{tx.supervisor_signature}</span>
              )}
            </div>
          </li>
        ))
      )}
    </ul>
  );
}

// — Routes & App wrapper —
function AppRoutes() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/worker"
          element={
            <Protected role="worker">
              <WorkerPage />
            </Protected>
          }
        />
        <Route
          path="/manager"
          element={
            <Protected role="manager">
              <ManagerPage />
            </Protected>
          }
        />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </Router>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}
