import "../styles/ResultCard.css";

function ResultCard({ result }) {

  if (!result) {
  return (
    <div className="result-card">
      <div className="status success">
        ✔ Ready for Deployment
      </div>

      <p>Click Deploy to start deployment.</p>
    </div>
  );
}

if (result.status === "failed" || result.status === "rejected") {
  return (
    <div className="result-card">
      <div className="status failed">
        ✖ Deployment Failed
      </div>

      <div className="result-section">
        <h3>Reason</h3>
        <p>{result.reason}</p>
      </div>
    </div>
  );
}

if (!result.cost_estimates) {
  return (
    <div className="result-card">
      <div className="status failed">
        ✖ Deployment Failed
      </div>

      <div className="result-section">
        <h3>Reason</h3>
        <p>{result.reason || "No cost estimates received."}</p>
      </div>
    </div>
  );
}

  return (
    <div className="result-card">

      <div className="status success">
        ✔ Deployment Successful
      </div>

      <div className="result-section">
        <h3>Selected Cloud</h3>
        <p>{result.selected_cloud}</p>
      </div>

      <div className="result-section">
        <h3>Estimated Costs</h3>

        <table>
          <tbody>

            <tr>
              <td>AWS</td>
              <td>₹ {result.cost_estimates.AWS?.estimated_cost ?? "N/A"}</td>
            </tr>

            <tr>
              <td>Azure</td>
              <td>₹ {result.cost_estimates.Azure?.estimated_cost ?? "N/A"}</td>
            </tr>

            <tr>
              <td>Google Cloud</td>
              <td>₹ {result.cost_estimates.GCP?.estimated_cost ?? "N/A"}</td>
            </tr>

          </tbody>
        </table>

      </div>

      <div className="result-section">
        <h3>Reason</h3>
        <p>{result.reason}</p>
      </div>

    </div>
  );
}

export default ResultCard;