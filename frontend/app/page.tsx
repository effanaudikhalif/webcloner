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
      console.log("🌐 Making request to backend...");
      const res = await fetch("http://localhost:8000/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url }),
      });

      console.log("📡 Response received:", res.status, res.statusText);

      if (res.ok) {
        console.log("✅ Request successful, parsing response...");
        const data = await res.json();
        console.log("📦 Response data:", {
          htmlLength: data.html?.length || 0,
          cssLength: data.css?.length || 0,
          combinedLength: data.combined_html?.length || 0
        });
        
        setHtml(data.html);
        setCss(data.css);
        setCombinedHtml(data.combined_html);
        console.log("🎉 Cloning completed successfully!");
      } else {
        console.log("❌ Request failed:", res.status, res.statusText);
        const errorText = await res.text();
        console.log("📄 Error response:", errorText);
        setError(`Failed to generate clone: ${res.status} ${res.statusText}`);
        alert("Failed to generate clone.");
      }
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
          <iframe
            srcDoc={combinedHtml}
            style={{
              width: "100%",
              height: "600px",
              border: "1px solid #333",
              marginTop: "1rem",
              backgroundColor: "white",
            }}
            title="Cloned Preview"
          ></iframe>

          <div style={{ marginTop: "2rem" }}>
            <h3 style={{ fontSize: "1.25rem", marginBottom: "0.5rem" }}>
              Combined HTML
            </h3>
            <pre
              style={{
                backgroundColor: "#fff",
                color: "#000",
                padding: "1rem",
                borderRadius: "5px",
                overflowX: "auto",
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
