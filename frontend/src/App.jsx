import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Welcome              from "./pages/Welcome";
import Intake               from "./pages/Intake";
import Discovery            from "./pages/Discovery";
import DeepAssessment       from "./pages/DeepAssessment";
import Results              from "./pages/Results";
import Facilitator          from "./pages/Facilitator";
import MentorMatch          from "./pages/MentorMatch";
import Dashboard            from "./pages/Dashboard";
import Login                from "./pages/Login";
import InventIt             from "./pages/InventIt";
import InventItFacilitator  from "./pages/InventItFacilitator";
import InventItAdmin        from "./pages/InventItAdmin";
import ArtSpark             from "./pages/ArtSpark";
import Nav                  from "./components/Nav";
import "./App.css";

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <Nav />
        <main className="app-main">
          <Routes>
            <Route path="/"               element={<Welcome />} />
            <Route path="/intake"         element={<Intake />} />
            <Route path="/discovery/:sid" element={<Discovery />} />
            <Route path="/assess/:sid"    element={<DeepAssessment />} />
            <Route path="/results/:sid"   element={<Results />} />
            <Route path="/facilitator/:sid" element={<Facilitator />} />
            <Route path="/mentor/:cid"    element={<MentorMatch />} />
            <Route path="/dashboard"                  element={<Dashboard />} />
            <Route path="/login"                      element={<Login />} />
            <Route path="/invent-it"                  element={<InventIt />} />
            <Route path="/invent-it/:sid"             element={<InventIt />} />
            <Route path="/invent-it-facilitator/:sessionId" element={<InventItFacilitator />} />
            <Route path="/invent-it-admin"            element={<InventItAdmin />} />
            <Route path="/art-spark"                  element={<ArtSpark />} />
            <Route path="/art-spark/:uuid"            element={<ArtSpark />} />
            <Route path="*"                           element={<Navigate to="/" />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
