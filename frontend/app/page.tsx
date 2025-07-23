"use client";

import React, { useState } from "react";

export default function CloneSiteApp() {
  const [url, setUrl] = useState("");
  const [html, setHtml] = useState("");
  const [css, setCss] = useState("");
  const [combinedHtml, setCombinedHtml] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleGenerate = async () => {
    console.log("🚀 Generate Clone button clicked!");
    console.log("📝 URL to clone:", url);
    
    if (!url) {
      console.log("❌ No URL provided");
      alert("Please enter a URL to clone.");
      return;
    }

    setIsLoading(true);
    setError("");
    console.log("⏳ Starting cloning process...");

    try {
      console.log("📡 Sending request to backend...");
      const response = await fetch("http://localhost:8000/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url }),
      });

      console.log("📥 Response received:", response.status, response.statusText);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error("❌ Backend error:", errorText);
        throw new Error(`Backend error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      console.log("📊 Response data:", {
        htmlLength: data.html?.length || 0,
        cssLength: data.css?.length || 0,
        combinedLength: data.combined_html?.length || 0,
        hasHtml: !!data.html,
        hasCss: !!data.css,
        hasCombined: !!data.combined_html
      });

      if (!data.combined_html) {
        console.error("❌ No combined HTML in response");
        throw new Error("No HTML content received from backend");
      }

      setCombinedHtml(data.combined_html);
      console.log("✅ Combined HTML set:", data.combined_html.length, "characters");
    } catch (error: any) {
      console.log("💥 Exception occurred:", error);
      setError(`Network error: ${error.message || 'Unknown error'}`);
      alert("Failed to generate clone.");
    } finally {
      setIsLoading(false);
      console.log("🏁 Cloning process finished");
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        backgroundColor: "#000", // black background
        padding: "2rem",
        color: "white",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <h1 style={{ fontSize: "2rem", marginBottom: "1rem" }}>
        Website Cloner
      </h1>
      <div style={{ display: "flex", gap: "1rem", marginBottom: "1rem" }}>
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Enter website URL..."
          style={{
            flex: 1,
            padding: "0.5rem",
            borderRadius: "5px",
            border: "1px solid #ccc",
          }}
        />
        <button
          onClick={handleGenerate}
          disabled={isLoading}
          style={{
            padding: "0.5rem 1rem",
            backgroundColor: isLoading ? "#666" : "#4CAF50",
            color: "white",
            border: "none",
            borderRadius: "5px",
            cursor: isLoading ? "not-allowed" : "pointer",
          }}
        >
          {isLoading ? "Cloning..." : "Generate Clone"}
        </button>
      </div>

      {error && (
        <div style={{ 
          backgroundColor: "#ff4444", 
          color: "white", 
          padding: "1rem", 
          borderRadius: "5px", 
          marginBottom: "1rem" 
        }}>
          Error: {error}
        </div>
      )}

      {combinedHtml && (
        <>
          <h2 style={{ fontSize: "1.5rem", marginTop: "2rem" }}>
            Preview of Cloned Website
          </h2>
          <div style={{ 
            border: "1px solid #333", 
            marginTop: "1rem",
            backgroundColor: "white",
            borderRadius: "5px",
            overflow: "hidden"
          }}>
            <iframe
              srcDoc={combinedHtml}
              style={{
                width: "100%",
                height: "600px",
                border: "none",
                display: "block"
              }}
              title="Cloned Preview"
              sandbox="allow-scripts allow-same-origin"
              onLoad={() => console.log("✅ Iframe loaded successfully")}
              onError={(e) => console.error("❌ Iframe error:", e)}
            />
          </div>

          <div style={{ marginTop: "2rem" }}>
            <h3 style={{ fontSize: "1.25rem", marginBottom: "0.5rem" }}>
              Generated HTML (with CSS)
            </h3>
            <pre
              style={{
                backgroundColor: "#fff",
                color: "#000",
                padding: "1rem",
                borderRadius: "5px",
                overflowX: "auto",
                maxHeight: "400px",
                overflowY: "auto",
                fontSize: "0.8rem"
              }}
            >
              {combinedHtml}
            </pre>
          </div>
        </>
      )}
    </div>
  );
}
