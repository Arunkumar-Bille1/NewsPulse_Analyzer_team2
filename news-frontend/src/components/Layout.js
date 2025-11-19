import React from "react";
import Navbar from "./Navbar";
import Sidebar from "./Sidebar";

function Layout({ children }) {
  return (
    <div className="bg-gray-50 min-h-screen">

      {/* Global Navbar */}
      <Navbar />

      {/* Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="ml-64 pt-20 px-8 pb-10">
        {children}
      </div>

    </div>
  );
}

export default Layout;
