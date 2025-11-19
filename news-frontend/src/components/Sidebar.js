import React from "react";
import { NavLink } from "react-router-dom";

// Importing Icons
import homeIcon from "../assets/icons/home.jpeg";
import trendingIcon from "../assets/icons/trending.jpeg";
import explorerIcon from "../assets/icons/sentiment analysis.jpeg";
import textIcon from "../assets/icons/trendexplorer.jpeg";
import compareIcon from "../assets/icons/compare.jpeg";
import bookmarkIcon from "../assets/icons/bookmark.jpeg";
import settingsIcon from "../assets/icons/settings.jpeg";

export default function Sidebar() {
  const menu = [
    { name: "Dashboard", path: "/", icon: homeIcon },
    { name: "Trending News", path: "/trending", icon: trendingIcon },
    { name: "Trend Explorer", path: "/topic-trends", icon: explorerIcon },
    { name: "Text Analysis", path: "/analyze", icon: textIcon },
    { name: "Compare Articles", path: "/compare", icon: compareIcon },
    { name: "Bookmark", path: "/SavedNews", icon: bookmarkIcon },
    { name: "Settings", path: "/Settings", icon: settingsIcon },
  ];

  return (
    <div className="fixed left-0 top-0 w-64 h-full bg-white shadow-lg border-r flex flex-col py-8 z-50">

      {/* Brand Title */}
      <div className="text-center mb-10">
        <h1 className="text-3xl font-extrabold text-indigo-600 tracking-wide">
          TrendVista
        </h1>
      </div>

      {/* Navigation Items */}
      <nav className="flex flex-col gap-1 px-4">
        {menu.map((item) => (
          <NavLink
            key={item.name}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-4 px-4 py-3 rounded-lg transition-all 
              ${
                isActive
                  ? "bg-indigo-100 text-indigo-700 font-semibold shadow-sm"
                  : "text-gray-700 hover:bg-indigo-50 hover:text-indigo-700"
              }`
            }
          >
            <img
              src={item.icon}
              alt={item.name}
              className="w-6 h-6 object-contain"
            />
            <span className="text-[15px]">{item.name}</span>
          </NavLink>
        ))}
      </nav>

    </div>
  );
}
