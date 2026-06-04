// API helper — all calls to the backend in one place
export const BASE = "https://tins-v2-1.onrender.com/api";

async function req(method, path, body) {
  const token = localStorage.getItem("goat_token");
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

export const api = {
  // Auth
  login:         (data)      => req("POST", "/auth/login", data),
  me:            ()          => req("GET",  "/auth/me"),
  logout:        ()          => req("POST", "/auth/logout"),
  changePassword:(data)      => req("POST", "/auth/change-password", data),
  loginSupabase: (data)      => req("POST", "/auth/login-supabase", data),
  register:      (data)      => req("POST", "/auth/register", data),

  // Children
  getChildren:    ()          => req("GET",  "/children"),
  getChild:       (id)        => req("GET",  `/children/${id}`),
  createChild:    (data)      => req("POST", "/children", data),
  childSessions:  (id)        => req("GET",  `/children/${id}/sessions`),
  childMatches:   (id)        => req("GET",  `/matches/child/${id}`),

  // Sessions
  createSession:  (child_id)  => req("POST", "/sessions", { child_id }),
  submitSession:  (id, data)  => req("POST", `/sessions/${id}/submit`, data),
  analyzeSession: (id, data)  => req("POST", `/sessions/${id}/analyze`, data),
  getSession:     (id)        => req("GET",  `/sessions/${id}`),
  submitDiscovery:(id, data)  => req("POST", `/sessions/${id}/discovery`, data),

  // Facilitator
  addNote:        (data)      => req("POST", "/notes", data),
  getNotes:       (sid)       => req("GET",  `/notes/session/${sid}`),

  // Mentors
  getMentors:     (domain)    => req("GET",  `/mentors${domain ? `?domain=${domain}` : ""}`),
  createMatch:    (data)      => req("POST", "/matches", data),
  updateMilestone:(mid, data) => req("PUT",  `/matches/${mid}/milestone`, data),

  // Stats
  getStats:       ()          => req("GET",  "/stats"),

  // TMS Extensions
  getUsers:        ()          => req("GET",  "/admin/users"),
  createUser:      (data)      => req("POST", "/admin/users", data),
  deleteUser:      (id)        => req("DELETE", `/admin/users/${id}`),
  approveUser:     (id, data)  => req("PUT",    `/admin/users/${id}/approve`, data),
  getCenters:      ()          => req("GET",  "/centers"),
  createCenter:    (data)      => req("POST", "/centers", data),
  getWorkshops:    ()          => req("GET",  "/workshops"),
  createWorkshop:  (data)      => req("POST", "/workshops", data),
  getWorkshopSessions:(wid)    => req("GET",  `/workshops/${wid}/sessions`),
  createWorkshopSession:(wid, d) => req("POST", `/workshops/${wid}/sessions`, d),
  getStudentAttendance:(cid)   => req("GET",  `/workshops/attendance/${cid}`),
  getMentorValidations:(cid)   => req("GET",  `/mentors/validations/${cid}`),
  submitMentorValidation:(data)=> req("POST", "/mentors/validations", data),
  getPuzzles:      ()          => req("GET",  "/puzzles"),
  editPuzzle:      (pid, data) => req("PUT",  `/puzzles/${pid}`, data),
  scheduleReassessment:(cid)   => req("POST", "/sessions/reassess", { child_id: cid }),
  getAnalytics:    ()          => req("GET",  "/analytics"),
};

