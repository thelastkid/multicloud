import { useState } from "react";
import "./styles/App.css";

import DeploymentForm from "./components/DeploymentForm";
import ResultCard from "./components/ResultCard";

function App() {
  const [result, setResult] = useState(null);

  return (
    <div className="app">
      <div className="container">

        <header className="header">
          <h1>Multi-Cloud Infrastructure Dashboard</h1>
          <p>AI-Powered Multi-Cloud Deployment Platform</p>
        </header>

        <div className="dashboard">

          <div className="card">
            <h2>Deployment Form</h2>

            <DeploymentForm
              setResult={setResult}
            />

          </div>

          <div className="card">
            <h2>Deployment Result</h2>

            <ResultCard
              result={result}
            />

          </div>

        </div>

      </div>
    </div>
  );
}

export default App;